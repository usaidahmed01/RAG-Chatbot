"""
Chainlit user interface for the FIFA 26 Football RAG Chatbot.

The premium landing UI is injected from public/custom.js.
This file keeps the Python side clean and focused on RAG logic.
"""

from typing import Any

import chainlit as cl

from rag_chain import MISSING_INFO_RESPONSE, ask_rag


PROJECT_TITLE = "FIFA 26 Football RAG Chatbot"

def format_sources_for_display(
    sources: list[dict[str, Any]],
) -> str:
    """
    Convert retrieved source metadata into user-friendly source summaries.

    This version avoids showing technical chunk details to the user.
    It keeps source transparency but presents it in a clean way.
    """

    if not sources:
        return """
## 📚 Sources Used

> No matching source evidence was found in the local football knowledge base.
"""

    unique_sources: list[dict[str, Any]] = []
    seen_sources: set[str] = set()

    for source in sources:
        title = source.get("title", "Unknown title")
        source_url = source.get("source_url", "")
        unique_key = f"{title}-{source_url}"

        if unique_key in seen_sources:
            continue

        seen_sources.add(unique_key)
        unique_sources.append(source)

    source_lines = ["\n\n## 📚 Sources Used"]

    for source in unique_sources[:3]:
        title = source.get("title", "Unknown title")
        source_url = source.get("source_url", "")
        preview = source.get("retrieved_preview", "").strip()

        if len(preview) > 320:
            preview = preview[:320].rstrip() + "..."

        source_lines.append(
            f"""
### ⚽ {title}

**Why this source was used:**  
This source contains relevant football or FIFA World Cup information retrieved from the local knowledge base for your question.

**Source link:**  
{source_url}

**Evidence Preview**

> {preview}
"""
        )

    return "\n".join(source_lines)

@cl.on_chat_start
async def on_chat_start() -> None:
    """
    Runs once when the user opens the chatbot.

    The main hero section is injected by public/custom.js.
    This message is intentionally minimal so the UI does not look duplicated.
    """

    await cl.Message(
        content=(
            "⚽ **Football RAG system is ready.**\n\n"
            "Ask a question about football, FIFA World Cup history, records, hosts, "
            "or the 2026 FIFA World Cup."
        )
    ).send()


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
        content="⚽ Searching match archives and retrieving verified football evidence..."
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

> {answer}

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