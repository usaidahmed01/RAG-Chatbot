"""Download open-source football articles from Wikipedia."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

DATA_DIRECTORY = Path("data")
SOURCES_FILE = DATA_DIRECTORY / "sources.json"

MINIMUM_ARTICLE_LENGTH = 1_000

REQUEST_HEADERS = {
    "User-Agent": (
        "RAGChatbot/1.0 "
        "contact: usaid423@gmail.com"
    )
}

# Wikipedia articles that will form our football knowledge base.
ARTICLE_TITLES = [
    "Association football",
    "FIFA World Cup",
    "History of the FIFA World Cup",
    "2026 FIFA World Cup",
    "2022 FIFA World Cup",
    "FIFA World Cup records and statistics",
    "List of FIFA World Cup finals",
    "List of FIFA World Cup hosts",
    "FIFA World Cup qualification",
]

def create_safe_filename(title: str) -> str:

    filename = title.lower()
    filename = re.sub(r"[^a-z0-9]+", "_", filename)
    filename = filename.strip("_")

    return f"{filename}.txt"

def fetch_wikipedia_article(
    title: str,
    session: requests.Session,
) -> dict[str, Any]:
    """Download one Wikipedia article through the MediaWiki API."""

    parameters = {
        "action": "query",
        "prop": "extracts|info",
        "titles": title,
        "explaintext": True,
        "exsectionformat": "plain",
        "inprop": "url",
        "redirects": True,
        "format": "json",
        "formatversion": 2,
    }

    response = session.get(
        WIKIPEDIA_API_URL,
        params=parameters,
        timeout=30,
    )

    response.raise_for_status()

    response_data = response.json()
    # print("response: ",response_data)
    pages = response_data.get("query", {}).get("pages", [])

    if not pages:
        raise ValueError(f"No Wikipedia page was returned for: {title}")

    page = pages[0]

    if page.get("missing"):
        raise ValueError(f"Wikipedia article does not exist: {title}")

    article_text = page.get("extract", "").strip()

    if len(article_text) < MINIMUM_ARTICLE_LENGTH:
        raise ValueError(
            f"Article '{title}' is too short or empty. "
            f"Received only {len(article_text)} characters."
        )

    return {
        "title": page.get("title", title),
        "text": article_text,
        "source_url": page.get("fullurl", ""),
        "page_id": page.get("pageid"),
    }

def save_article(article: dict[str, Any]) -> dict[str, Any]:
    """Save one downloaded article as a text file."""

    filename = create_safe_filename(article["title"])
    file_path = DATA_DIRECTORY / filename

    file_path.write_text(
        article["text"],
        encoding="utf-8",
    )

    return {
        "title": article["title"],
        "filename": filename,
        "source_url": article["source_url"],
        "page_id": article["page_id"],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "license": "Creative Commons Attribution-ShareAlike",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "character_count": len(article["text"]),
    }

def save_sources_metadata(sources: list[dict[str, Any]]):
    """
    Save attribution and source details for all downloaded articles.
    """

    metadata = {
        "dataset_name": "Football and FIFA World Cup Wikipedia Dataset",
        "dataset_description": (
            "A collection of publicly available Wikipedia articles "
            "related to association football and the FIFA World Cup."
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(sources),
        "sources": sources,
    }

    SOURCES_FILE.write_text(
        json.dumps(metadata, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

def main():

    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

    downloaded_sources: list[dict[str, Any]] = []
    failed_articles: list[str] = []

    with requests.Session() as session:
        session.headers.update(REQUEST_HEADERS)

        for article_title in ARTICLE_TITLES:
            print(f"Downloading: {article_title}")

            try:
                article = fetch_wikipedia_article(
                    title=article_title,
                    session=session,
                )

                source_metadata = save_article(article)
                downloaded_sources.append(source_metadata)

                print(
                    f"Saved: {source_metadata['filename']} "
                    f"({source_metadata['character_count']:,} characters)"
                )

            except (requests.RequestException, ValueError) as error:
                failed_articles.append(article_title)
                print(f"Failed to download '{article_title}': {error}")

    save_sources_metadata(downloaded_sources)

    print("\nDataset download completed.")
    print(f"Successfully downloaded: {len(downloaded_sources)} articles")
    print(f"Failed downloads: {len(failed_articles)}")
    print(f"Source metadata saved to: {SOURCES_FILE}")

    if failed_articles:
        print("\nFailed article titles:")

        for article_title in failed_articles:
            print(f"- {article_title}")

main()
