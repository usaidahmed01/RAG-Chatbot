"""Build the Football RAG vector database."""

import hashlib
import json
import re
import shutil # manage file operations
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer


DATA_DIRECTORY = Path("data")
SOURCES_FILE = DATA_DIRECTORY / "sources.json"
CHROMA_DIRECTORY = Path("chroma_db")

COLLECTION_NAME = "football_knowledge_base"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50

def clean_text(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    cleaned_lines = []

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    print("Cleaned text: " , text)
    return text.strip()

def load_source_metadata() -> dict[str, dict[str, Any]]:

    if not SOURCES_FILE.exists():
        raise FileNotFoundError(
            f"Source metadata file was not found: {SOURCES_FILE}. "
            "Run download_data.py before running ingest.py."
        )

    metadata_content = SOURCES_FILE.read_text(encoding="utf-8")
    metadata = json.loads(metadata_content)

    sources = metadata.get("sources", [])

    if not sources:
        raise ValueError(
            f"No source records were found inside {SOURCES_FILE}."
        )

    return {
        source["filename"]: source
        for source in sources
    }

def load_documents(
    source_metadata: dict[str, dict[str, Any]],
) -> list[Document]:

    text_files = sorted(DATA_DIRECTORY.glob("*.txt"))

    if not text_files:
        raise FileNotFoundError(
            f"No .txt files were found inside {DATA_DIRECTORY}. "
            "Run download_data.py before running ingest.py."
        )

    documents: list[Document] = []

    for text_file in text_files:
        raw_text = text_file.read_text(encoding="utf-8")
        cleaned_text = clean_text(raw_text)

        if not cleaned_text:
            print(f"Skipping empty file: {text_file.name}")
            continue

        source = source_metadata.get(text_file.name, {})

        document = Document(
            page_content=cleaned_text,
            metadata={
                "title": source.get(
                    "title",
                    text_file.stem.replace("_", " ").title(),
                ),
                "filename": text_file.name,
                "source_url": source.get("source_url", ""),
                "license": source.get("license", ""),
                "retrieved_at": source.get("retrieved_at", ""),
            },
        )

        documents.append(document)

    if not documents:
        raise ValueError("No valid documents were available for ingestion.")

    return documents

def create_chunk_id(
    filename: str,
    chunk_index: int,
    content: str,
) -> str:
    
    unique_value = f"{filename}:{chunk_index}:{content}"

    return hashlib.sha256(
        unique_value.encode("utf-8")
    ).hexdigest()

def create_chunks(
    documents: list[Document],
) -> tuple[list[Document], list[str]]:

    tokenizer = AutoTokenizer.from_pretrained(
        EMBEDDING_MODEL_NAME
    )

    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer=tokenizer,
        chunk_size=CHUNK_SIZE_TOKENS,
        chunk_overlap=CHUNK_OVERLAP_TOKENS,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: list[Document] = []
    all_chunk_ids: list[str] = []

    for document in documents:
        document_chunks = text_splitter.split_documents([document])
        total_chunks = len(document_chunks)

        for chunk_index, chunk in enumerate(document_chunks):
            chunk_id = create_chunk_id(
                filename=document.metadata["filename"],
                chunk_index=chunk_index,
                content=chunk.page_content,
            )

            chunk.metadata.update(
                {
                    "chunk_id": chunk_id,
                    "chunk_index": chunk_index,
                    "total_chunks": total_chunks,
                    "embedding_model": EMBEDDING_MODEL_NAME,
                    "chunk_size_tokens": CHUNK_SIZE_TOKENS,
                    "chunk_overlap_tokens": CHUNK_OVERLAP_TOKENS,
                }
            )

            all_chunks.append(chunk)
            all_chunk_ids.append(chunk_id)

    if not all_chunks:
        raise ValueError("No chunks were created from the loaded documents.")

    print("Chunk_id: " , all_chunk_ids[0])
    print("Chunk: " , all_chunks[0])

    return all_chunks, all_chunk_ids

def create_embeddings() -> HuggingFaceEmbeddings:

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )

def rebuild_vector_database(
    chunks: list[Document],
    chunk_ids: list[str],
    embeddings: HuggingFaceEmbeddings,
) -> Chroma:
    """
    Delete any previous local vector database and build a fresh one.
    """

    if CHROMA_DIRECTORY.exists():
        print(f"Removing old vector database: {CHROMA_DIRECTORY}")
        shutil.rmtree(CHROMA_DIRECTORY)

    vector_database = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=chunk_ids,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIRECTORY),
        collection_metadata={
            "hnsw:space": "cosine",
        },
    )

    return vector_database

def main() -> None:
    """
    Execute the complete ingestion pipeline.
    """

    print("Starting Football RAG ingestion pipeline...\n")

    print("1. Loading source metadata...")
    source_metadata = load_source_metadata()
    print(f"   Loaded metadata for {len(source_metadata)} sources.")

    print("\n2. Loading and cleaning documents...")
    documents = load_documents(source_metadata)
    print(f"   Loaded {len(documents)} valid documents.")

    print("\n3. Creating token-based chunks...")
    chunks, chunk_ids = create_chunks(documents)
    print(f"   Created {len(chunks)} chunks.")
    print(f"   Chunk size: {CHUNK_SIZE_TOKENS} tokens.")
    print(f"   Chunk overlap: {CHUNK_OVERLAP_TOKENS} tokens.")

    print("\n4. Loading embedding model...")
    embeddings = create_embeddings()
    print(f"   Embedding model: {EMBEDDING_MODEL_NAME}")

    print("\n5. Creating Chroma vector database...")
    vector_database = rebuild_vector_database(
        chunks=chunks,
        chunk_ids=chunk_ids,
        embeddings=embeddings,
    )

    stored_records = vector_database._collection.count()

    print("\nIngestion completed successfully.")
    print(f"Stored vector records: {stored_records}")
    print(f"Vector database location: {CHROMA_DIRECTORY}")
    print(f"Chroma collection: {COLLECTION_NAME}")

main()