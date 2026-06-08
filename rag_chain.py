
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()


CHROMA_DIRECTORY = Path("chroma_db")
COLLECTION_NAME = "football_knowledge_base"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_RETRIEVAL_K = 5

MISSING_INFO_RESPONSE = (
    "The requested target info is missing from the provided dataset."
)


STRICT_RAG_PROMPT = """
You are an objective football knowledge assistant.

Your task is to answer the user's question using ONLY the verified source context fragments provided below.

Rules:
1. Use only the provided context.
2. Do not use outside knowledge.
3. Do not guess or predict.
4. Do not add facts that are not directly supported by the context.
5. If the answer cannot be confidently found in the context, reply exactly:
"The requested target info is missing from the provided dataset."

[VERIFIED SOURCE CONTEXT]
{context}

[USER QUESTION]
{question}

Final answer:
"""

def create_embeddings() -> HuggingFaceEmbeddings:
    """Create the same embedding model used during ingestion. """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": "cpu",
            "token": os.getenv("HF_TOKEN"),
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )

def load_vector_database() -> Chroma:
    """Load the existing Chroma vector database from disk."""

    if not CHROMA_DIRECTORY.exists():
        raise FileNotFoundError(
            f"Vector database folder not found: {CHROMA_DIRECTORY}. "
            "Run ingest.py before running the chatbot."
        )

    embeddings = create_embeddings()

    vector_database = Chroma(
        persist_directory=str(CHROMA_DIRECTORY),
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    if vector_database._collection.count() == 0:
        raise ValueError(
            "The Chroma collection is empty. Run ingest.py again."
        )

    return vector_database

def format_context(documents: list[Document]) -> str:
    """Convert retrieved documents into a clean context string for the LLM. Each chunk includes source metadata so the model can ground its answer."""

    formatted_chunks = []

    for index, document in enumerate(documents, start=1):
        title = document.metadata.get("title", "Unknown title")
        source_url = document.metadata.get("source_url", "Unknown URL")
        filename = document.metadata.get("filename", "Unknown file")
        chunk_index = document.metadata.get("chunk_index", "Unknown chunk")

        formatted_chunk = (
            f"Source Chunk {index}\n"
            f"Title: {title}\n"
            f"Filename: {filename}\n"
            f"Chunk Index: {chunk_index}\n"
            f"Source URL: {source_url}\n"
            f"Content:\n{document.page_content}"
        )

        formatted_chunks.append(formatted_chunk)

    return "\n\n---\n\n".join(formatted_chunks)

def extract_sources(documents: list[Document]) -> list[dict[str, Any]]:
    """Extract readable source metadata from retrieved documents for Chainlit UI."""

    sources = []

    for document in documents:
        source = {
            "title": document.metadata.get("title", "Unknown title"),
            "filename": document.metadata.get("filename", "Unknown file"),
            "source_url": document.metadata.get("source_url", ""),
            "chunk_index": document.metadata.get("chunk_index", ""),
            "total_chunks": document.metadata.get("total_chunks", ""),
            "retrieved_preview": document.page_content[:300].strip(),
        }

        sources.append(source)

    return sources

def create_llm() -> ChatGroq:

    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise EnvironmentError(
            "GROQ_API_KEY was not found."
        )

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0.2,
        api_key=groq_api_key,
    )

def retrieve_documents(
    question: str,
    k: int = DEFAULT_RETRIEVAL_K,
) -> list[Document]:
    """Retrieve the top-k most relevant chunks from ChromaDB. The vector database uses cosine similarity because that was configured during ingestion."""

    vector_database = load_vector_database()

    retriever = vector_database.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
        },
    )

    return retriever.invoke(question)

def ask_rag(
    question: str,
    k: int = DEFAULT_RETRIEVAL_K,
) -> dict[str, Any]:
    """It receives a question and returns:
    - answer
    - retrieved sources
    - number of retrieved chunks"""

    cleaned_question = question.strip()

    if not cleaned_question:
        return {
            "answer": "Please enter a valid question.",
            "sources": [],
            "retrieved_chunk_count": 0,
        }

    retrieved_documents = retrieve_documents(
        question=cleaned_question,
        k=k,
    )

    if not retrieved_documents:
        return {
            "answer": MISSING_INFO_RESPONSE,
            "sources": [],
            "retrieved_chunk_count": 0,
        }

    context = format_context(retrieved_documents)
    sources = extract_sources(retrieved_documents)

    prompt = ChatPromptTemplate.from_template(STRICT_RAG_PROMPT)
    llm = create_llm()

    rag_chain = prompt | llm | StrOutputParser()

    answer = rag_chain.invoke(
        {
            "context": context,
            "question": cleaned_question,
        }
    )

    return {
        "answer": answer.strip(),
        "sources": sources,
        "retrieved_chunk_count": len(retrieved_documents),
    }


def main():
    test_question = "Who will win the 2026 FIFA World Cup?"

    response = ask_rag(test_question)

    print("\nQuestion:")
    print(test_question)

    print("\nAnswer:")
    print(response["answer"])

    print("\nRetrieved Sources:")
    for source in response["sources"]:
        print(
            f"- {source['title']} "
            f"(chunk {source['chunk_index']})"
        )

main()