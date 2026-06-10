# RAG Architecture Diagram

```mermaid
flowchart TD
    A["Wikipedia Articles<br/>Football + FIFA World Cup Topics"] --> B["download_data.py"]

    B --> C["data/*.txt<br/>Raw Article Text"]
    B --> D["data/sources.json<br/>Source Metadata"]

    C --> E["ingest.py"]
    D --> E

    E --> F["Text Cleaning<br/>Remove extra spaces + invalid characters"]
    F --> G["Token Chunking<br/>500 tokens + 50 overlap"]

    G --> H["HuggingFace Embeddings<br/>all-MiniLM-L6-v2"]

    H --> I["ChromaDB Vector Database<br/>chroma_db/"]

    J["User Question"] --> K["app.py<br/>Chainlit UI"]

    K --> L["rag_chain.py"]

    L --> M["Embed User Question"]
    M --> N["Semantic Search<br/>Top-k Relevant Chunks"]

    I --> N

    N --> O["Retrieved Context<br/>Relevant Source Chunks"]

    O --> P["Strict RAG Prompt<br/>Use only retrieved context"]

    P --> Q["Groq LLM<br/>llama-3.1-8b-instant"]

    Q --> R["Grounded Answer"]

    O --> S["Source Summary<br/>Evidence Preview"]

    R --> T["Final UI Response"]
    S --> T

    T --> U["Answer + Sources<br/>Displayed in Chainlit"]