"""
Chainlit user interface for the FIFA 26 Football RAG Chatbot.
"""

from typing import Any

import chainlit as cl

from rag_chain import MISSING_INFO_RESPONSE, ask_rag


PROJECT_TITLE = "FIFA 26 Football RAG Chatbot"
PROJECT_DESCRIPTION = """
A football-themed Retrieval-Augmented Generation chatbot focused on
football, FIFA World Cup history, and the 2026 FIFA World Cup.

Built with LangChain, ChromaDB, HuggingFace embeddings, Groq LLM, and Chainlit.
"""

LOGO_PATH = "/public/fifa26-logo.png"


def format_sources_for_display(
    sources: list[dict[str, Any]],
) -> str:
    """
    Convert retrieved source metadata into themed HTML cards.
    """

    if not sources:
        return """
## 🏟️ Top Match Sources

<div class="fifa-source-card">
  <div class="fifa-source-title">No source chunks retrieved</div>
  <div class="fifa-source-meta">
    The system did not find relevant chunks for this question.
  </div>
</div>
"""

    source_lines = ["\n\n## 🏟️ Top Match Sources"]

    for index, source in enumerate(sources, start=1):
        title = source.get("title", "Unknown title")
        filename = source.get("filename", "Unknown file")
        source_url = source.get("source_url", "")
        chunk_index = source.get("chunk_index", "Unknown")
        total_chunks = source.get("total_chunks", "Unknown")
        preview = source.get("retrieved_preview", "")

        source_lines.append(
            f"""
<div class="fifa-source-card">
  <div class="fifa-source-title">⚽ Source {index}: {title}</div>
  <div class="fifa-source-meta">
    <strong>File:</strong> <code>{filename}</code><br>
    <strong>Chunk:</strong> <code>{chunk_index}</code> of <code>{total_chunks}</code><br>
    <strong>URL:</strong> <a href="{source_url}" target="_blank">{source_url}</a>
  </div>

  <div class="fifa-source-preview-label">Evidence Preview</div>
  <blockquote>{preview}</blockquote>
</div>
"""
        )

    return "\n".join(source_lines)


@cl.on_chat_start
async def on_chat_start() -> None:
    """
    Runs once when the user opens the chatbot.
    """

    welcome_message = f"""
<p align="center">
  <img src="{LOGO_PATH}" alt="FIFA World Cup 2026 Logo" class="fifa-center-logo" />
</p>

<p align="center">
  <span class="fifa-badge">Football Knowledge Base · RAG System · World Cup 2026</span>
</p>

# {PROJECT_TITLE}

{PROJECT_DESCRIPTION}

## ⚽ Ask Football Questions

Try asking:

- Which countries are hosting the 2026 FIFA World Cup?
- Who won the 2022 FIFA World Cup?
- What is association football?
- How often is the FIFA World Cup held?
- What are some FIFA World Cup records?

## 🛡️ Grounded Answer Policy

This chatbot answers from retrieved Wikipedia dataset chunks only.

If the answer is not available in the retrieved context, it should reply:

`{MISSING_INFO_RESPONSE}`
"""

    await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """
    Runs every time the user sends a message.
    """

    user_question = message.content.strip()

    if not user_question:
        await cl.Message(
            content="Please enter a valid football or World Cup question."
        ).send()
        return

    loading_message = cl.Message(
        content="""
<div class="fifa-loading">
  <span class="fifa-loading-ball">⚽</span>
  <span class="fifa-loading-text">Searching the FIFA 26 football knowledge base...</span>
</div>
"""
    )
    await loading_message.send()

    try:
        result = ask_rag(user_question)

        answer = result["answer"]
        sources = result["sources"]
        retrieved_chunk_count = result["retrieved_chunk_count"]

        sources_markdown = format_sources_for_display(sources)

        final_response = f"""
## 🎯 Answer

{answer}

---

<div class="fifa-retrieved-badge">Retrieved Chunks: {retrieved_chunk_count}</div>

{sources_markdown}
"""

        loading_message.content = final_response
        await loading_message.update()

    except Exception as error:
        loading_message.content = (
            "The chatbot could not process your question.\n\n"
            f"Error details: `{str(error)}`"
        )
        await loading_message.update()