# Engineering Report

## FIFA 26 Football RAG Chatbot

---

## 1. Project Overview

The FIFA 26 Football RAG Chatbot is a Retrieval-Augmented Generation application designed to answer questions about football, FIFA World Cup history, records, hosts, qualification, and the 2026 FIFA World Cup.

The chatbot uses a local football knowledge base created from publicly available Wikipedia articles. Instead of relying only on the language model’s internal knowledge, the system retrieves relevant text chunks from the local vector database and then generates a grounded answer using only the retrieved context.

The goal of this project is to demonstrate a complete RAG pipeline with:

* Open-source dataset collection
* Text cleaning and preprocessing
* Token-based chunking
* Embedding generation
* Vector database storage
* Semantic retrieval
* Strict grounded prompting
* User-facing chatbot interface
* Source evidence display
* Hallucination control

---

## 2. Dataset Selection

The dataset is built using publicly available Wikipedia articles related to football and the FIFA World Cup.

The selected topics include:

* Association football
* FIFA World Cup
* History of the FIFA World Cup
* 2026 FIFA World Cup
* 2022 FIFA World Cup
* FIFA World Cup records and statistics
* List of FIFA World Cup finals
* List of FIFA World Cup hosts
* FIFA World Cup qualification

Wikipedia was selected because it is public, accessible, and suitable for educational and research-based projects. Each downloaded article is stored as a plain text file inside the `data/` directory.

The dataset metadata is stored in:

```text
data/sources.json
```

This metadata includes:

* Article title
* File name
* Source URL
* Page ID
* Retrieval timestamp
* License information
* Character count

This makes the dataset more transparent and reproducible.

---

## 3. Data Collection Process

The project uses a dedicated script:

```text
download_data.py
```

This script downloads the selected Wikipedia articles using the Wikipedia API and stores them locally as `.txt` files.

The data collection process follows these steps:

1. Define selected Wikipedia article titles.
2. Request article content from Wikipedia API.
3. Extract article text in plain text format.
4. Save each article inside the `data/` folder.
5. Store metadata in `data/sources.json`.

This approach makes the dataset reproducible because the project does not depend on manual copy-pasting.

---

## 4. Text Cleaning and Preprocessing

The text cleaning step is handled inside:

```text
ingest.py
```

The cleaning process removes unnecessary control characters, extra spaces, and excessive blank lines.

The purpose of cleaning is to improve the quality of chunks before embedding generation. Cleaner chunks help the retriever return more relevant results and reduce irrelevant context being sent to the LLM.

---

## 5. Chunking Strategy

The project uses token-based chunking.

Chunking configuration:

```text
Chunk size: 500 tokens
Chunk overlap: 50 tokens
```

The chunk overlap is approximately 10% of the chunk size.

The reason for using overlap is to preserve context between neighboring chunks. If an important sentence or paragraph is split between two chunks, the overlap helps avoid losing meaning.

Example:

```text
Chunk 1: Tokens 1–500
Chunk 2: Tokens 451–950
Chunk 3: Tokens 901–1400
```

This means the last 50 tokens of one chunk are repeated at the beginning of the next chunk.

---

## 6. Embedding Model

The project uses the HuggingFace embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

This model was selected because:

* It is free and open-source.
* It is lightweight and fast.
* It works well for semantic similarity search.
* It can run locally on CPU.
* It is suitable for educational RAG projects.

Embeddings convert text chunks into numerical vectors. These vectors allow the system to compare the meaning of the user’s question with the meaning of stored chunks.

---

## 7. Vector Database

The project uses:

```text
ChromaDB
```

ChromaDB stores the embedded chunks locally inside:

```text
chroma_db/
```

Each stored chunk includes:

* Chunk text
* Source title
* Source URL
* File name
* Chunk index
* Total chunk count
* Embedding model name
* Chunking configuration

The vector database is rebuilt using:

```text
python ingest.py
```

Before rebuilding, the old `chroma_db/` folder is removed to avoid duplicate records.

---

## 8. Retrieval Strategy

The system uses semantic similarity retrieval.

Current retrieval configuration:

```text
Search type: similarity
Top-k: 4
Similarity space: cosine
```

When the user asks a question, the system embeds the question and compares it with stored chunk embeddings. The most relevant chunks are retrieved and passed to the language model as context.

This allows the chatbot to answer from local evidence instead of relying only on general model knowledge.

---

## 9. LLM and Prompt Design

The project uses Groq as the LLM provider through LangChain.

The default model is:

```text
llama-3.1-8b-instant
```

The prompt is designed to be strict and grounded. It instructs the model to:

* Use only the provided retrieved context.
* Avoid outside knowledge.
* Avoid guessing.
* Avoid predictions.
* Return a fixed fallback response if the answer is missing.

Fallback response:

```text
The requested target info is missing from the provided dataset.
```

This strict prompt helps reduce hallucinations and improves trustworthiness.

---

## 10. User Interface

The project uses:

```text
Chainlit
```

The UI is customized with:

```text
public/styles.css
public/custom.js
```

The interface includes:

* Football-themed landing hero
* FIFA World Cup visual branding
* Football pitch-inspired background
* Animated football elements
* Suggested prompt cards
* Premium dark theme
* Custom send and stop buttons
* Answer-focused layout
* User-friendly source display

The source display is intentionally simplified for normal users. Instead of showing technical chunk details, the UI displays:

* Source title
* Short explanation of why the source was used
* Source URL
* Evidence preview

This keeps transparency while avoiding unnecessary technical complexity.

---

## 11. Source Evidence Display

Each answer includes supporting sources from the retrieved context.

The purpose of showing evidence is to make the chatbot more trustworthy. Users can see where the information came from and review the relevant preview.

The UI does not expose low-level details such as chunk IDs or total chunk counts because normal users usually care more about the answer and the source summary.

---

## 12. Hallucination Control

Hallucination control is one of the main goals of this project.

The system uses multiple techniques to reduce hallucination:

1. Local knowledge base retrieval
2. Strict prompt instructions
3. Fixed fallback response
4. Source evidence display
5. Manual hallucination test questions

Example hallucination control question:

```text
Who will win the 2026 FIFA World Cup?
```

Expected response:

```text
The requested target info is missing from the provided dataset.
```

The model should not predict future results.

---

## 13. Testing Strategy

Testing questions are stored in:

```text
tests/test_questions.md
```

The tests are divided into:

* Answerable questions
* Retrieval quality questions
* Hallucination control questions
* Unrelated questions
* Edge cases

The tests check whether:

* Answers are relevant
* Sources are shown
* Evidence previews are displayed
* The model avoids unsupported claims
* Missing information returns the fallback response
* The UI remains clean and user-friendly

---

## 14. Limitations

The project has some limitations:

1. The knowledge base is limited to selected Wikipedia articles.
2. The answer quality depends on the quality of retrieved chunks.
3. If the retriever fails to retrieve the correct context, the LLM may return the fallback response.
4. The current retriever uses simple top-k similarity search without reranking.
5. The chatbot does not continuously update the dataset unless `download_data.py` is run again.
6. The project focuses only on football and FIFA World Cup knowledge.

---

## 15. Future Improvements

Possible future improvements include:

* Add retrieval similarity score display for internal debugging.
* Add reranking using a free reranker model.
* Add hybrid search using vector search plus keyword search.
* Add more football data sources.
* Add automated evaluation script.
* Add model comparison between different Groq models.
* Add deployment using Docker.
* Add admin option to rebuild the vector database from UI.
* Add better logo transparency and final UI polish.
* Add screenshots and demo GIF in README.

---

## 16. Conclusion

The FIFA 26 Football RAG Chatbot demonstrates a complete end-to-end RAG workflow.

It collects public football data, processes it into clean chunks, stores embeddings in ChromaDB, retrieves relevant context using semantic search, and generates grounded answers using a strict LLM prompt.

The project is designed to be transparent, reproducible, and user-friendly. It includes source evidence, hallucination control, a polished football-themed UI, and structured testing material.

This makes the project suitable for academic evaluation, bootcamp demonstration, and portfolio presentation.
