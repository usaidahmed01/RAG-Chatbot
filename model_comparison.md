# Model Comparison

## FIFA 26 Football RAG Chatbot

This document compares different LLM options used with the FIFA 26 Football RAG Chatbot.

The goal of this comparison is to test:

- Answer accuracy
- Grounding quality
- Hallucination control
- Response speed
- Source usage
- User-facing answer quality

---

## 1. Models Tested

| Model | Provider | Purpose |
|---|---|---|
| `llama-3.1-8b-instant` | Groq | Default fast model |
| `llama-3.3-70b-versatile` | Groq | Stronger reasoning model |
| `openai/gpt-oss-20b` | Groq | Alternative open-weight model |

> Note: Availability of models may depend on the Groq account and dashboard. Use only the models available in your Groq console.

---

## 2. Testing Method

Each model was tested using the same dataset, same ChromaDB vector database, same embedding model, same reranker, and same strict RAG prompt.

Only the LLM model was changed.

The model was changed from the `.env` file:

```env
GROQ_MODEL=llama-3.1-8b-instant