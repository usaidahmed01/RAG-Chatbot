
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
from sentence_transformers import CrossEncoder


load_dotenv()


CHROMA_DIRECTORY = Path("chroma_db")
COLLECTION_NAME = "football_knowledge_base"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_RETRIEVAL_K = 5

RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RERANKER_CANDIDATE_K = 20

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
    """
    Extract clean source metadata for UI display.
    """

    sources = []

    for document in documents:
        source = {
            "title": document.metadata.get("title", "Unknown title"),
            "filename": document.metadata.get("filename", "Unknown file"),
            "source_url": document.metadata.get("source_url", ""),
            "chunk_index": document.metadata.get("chunk_index", ""),
            "total_chunks": document.metadata.get("total_chunks", ""),
            "retrieval_score": document.metadata.get("retrieval_score", ""),
            "rerank_score": document.metadata.get("rerank_score", ""),
            "source_confidence": document.metadata.get("source_confidence", "Unknown"),
            "retrieved_preview": document.page_content[:420].strip(),
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
        # model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        model=os.getenv("GROQ_MODEL"),

        temperature=0.3,
        api_key=groq_api_key,
    )

def convert_distance_to_confidence(score: float) -> str:
    """Convert ChromaDB cosine distance score into a user-friendly confidence label."""

    if score <= 0.35:
        return "High"
    if score <= 0.60:
        return "Medium"
    return "Low"


def create_reranker() -> CrossEncoder:
    """
    Load the cross-encoder reranker model.
    """
    return CrossEncoder(RERANKER_MODEL_NAME)

def rerank_documents(
    question: str,
    documents: list[Document],
    top_k: int = DEFAULT_RETRIEVAL_K,
) -> list[Document]:
    """
    Rerank retrieved documents using a cross-encoder reranker.ChromaDB first retrieves candidate chunks.The reranker then sorts those chunks by relevance to the user question.
    """

    if not documents:
        return []

    reranker = create_reranker()

    question_document_pairs = [
        [question, document.page_content]
        for document in documents
    ]

    rerank_scores = reranker.predict(question_document_pairs)

    scored_documents = []

    for document, rerank_score in zip(documents, rerank_scores):
        document.metadata["rerank_score"] = round(float(rerank_score), 4)
        scored_documents.append(document)

    scored_documents.sort(
        key=lambda document: document.metadata.get("rerank_score", 0),
        reverse=True,
    )

    return scored_documents[:top_k]

def expand_query(question: str) -> str:
    """
    Expand common football terms so retrieval can find related award pages.
    """

    expanded_question = question

    football_synonyms = {
        "top scorer": "Golden Boot leading goalscorer most goals",
        "top goalscorer": "Golden Boot leading goalscorer most goals",
        "highest scorer": "Golden Boot leading goalscorer most goals",
        "most goals": "Golden Boot leading goalscorer top scorer",
        "best player": "Golden Ball player of the tournament",
        "player of the tournament": "Golden Ball best player",
        "best goalkeeper": "Golden Glove Yashin Award goalkeeper of the tournament",
        "top assist": "most assists assist maker playmaker",
        "assist maker": "most assists top assists playmaker",
        "team of the tournament": "All-Star Team Dream Team team of the tournament",
        "young player": "Best Young Player Award",
        "fair play": "FIFA Fair Play Trophy",
        "scoreline": "final score result defeated won",
    }

    lower_question = question.lower()

    extra_terms = []

    for key_phrase, related_terms in football_synonyms.items():
        if key_phrase in lower_question:
            extra_terms.append(related_terms)

    if extra_terms:
        expanded_question = f"{question} {' '.join(extra_terms)}"

    return expanded_question

def retrieve_documents(
    question: str,
    k: int = DEFAULT_RETRIEVAL_K,
) -> list[Document]:
    """
    Retrieve and rerank the most relevant documents from ChromaDB.

    Step 1:
    Retrieve more candidate chunks from ChromaDB using vector similarity.

    Step 2:
    Use a cross-encoder reranker to select the best chunks.

    Step 3:
    Return the top-k reranked chunks to the RAG pipeline.
    """

    vector_database = load_vector_database()

    expended_question = expand_query(question)

    retrieved_results = vector_database.similarity_search_with_score(
        query=expended_question,
        k=RERANKER_CANDIDATE_K,
    )

    candidate_documents = []

    for document, score in retrieved_results:
        document.metadata["retrieval_score"] = round(float(score), 4)
        document.metadata["source_confidence"] = convert_distance_to_confidence(
            float(score)
        )
        candidate_documents.append(document)

    reranked_documents = rerank_documents(
        question=question,
        documents=candidate_documents,
        top_k=k,
    )

    return reranked_documents

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