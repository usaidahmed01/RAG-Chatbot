# FIFA 26 Football RAG Chatbot

A premium football-themed Retrieval-Augmented Generation chatbot focused on football, FIFA World Cup history, records, hosts, qualification, and the 2026 FIFA World Cup.

This project uses a local knowledge base created from public Wikipedia articles. It retrieves relevant context from a ChromaDB vector database and generates grounded answers using a Groq LLM through LangChain.

---

## Project Overview

This project demonstrates a complete end-to-end RAG pipeline.

The chatbot does not answer only from the LLM’s internal memory. Instead, it follows a grounded retrieval workflow:

1. Download public football-related Wikipedia articles.
2. Clean and preprocess the text.
3. Split text into token-based chunks.
4. Convert chunks into embeddings.
5. Store embeddings in ChromaDB.
6. Retrieve relevant chunks for each user question.
7. Send retrieved context to a strict LLM prompt.
8. Display the answer with user-friendly source evidence.

---

## Key Features

- Football and FIFA World Cup knowledge base
- Public Wikipedia dataset
- Reproducible data download script
- Token-based chunking with overlap
- HuggingFace sentence-transformer embeddings
- ChromaDB local vector database
- LangChain-based RAG pipeline
- Groq LLM integration
- Strict prompt for hallucination control
- Chainlit chatbot interface
- Premium football-themed UI
- Custom CSS and JavaScript
- Suggested prompt cards
- Source summaries and evidence previews
- Friendly fallback when information is missing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| RAG Framework | LangChain |
| Vector Database | ChromaDB |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| LLM Provider | Groq |
| Default LLM | `llama-3.1-8b-instant` |
| UI | Chainlit |
| Styling | Custom CSS |
| UI Enhancement | Custom JavaScript |
| Dataset Source | Wikipedia |

---

## Folder Structure

```text
football-rag-chatbot/
├── data/
│   ├── *.txt
│   └── sources.json
├── chroma_db/
├── public/
│   ├── styles.css
│   ├── custom.js
│   ├── fifa26-logo.png
│   ├── logo_dark.png
│   └── logo_light.png
├── tests/
│   └── test_questions.md
├── .chainlit/
│   └── config.toml
├── app.py
├── download_data.py
├── ingest.py
├── rag_chain.py
├── requirements.txt
├── .gitignore
├── engineering_report.md
└── README.md

---

## Architecture Diagram

The complete RAG workflow is documented here:

```text
architecture/rag_architecture.md