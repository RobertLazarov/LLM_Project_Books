
from __future__ import annotations

import json
import os
from typing import List, Dict, Any

from openai import OpenAI
from .vector_store import get_chroma_collection, index_books, semantic_search


DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "book_summaries.json")


def load_data() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_or_load_store(client: OpenAI, rebuild: bool = False):
    collection = get_chroma_collection(client=client, rebuild=rebuild)
    if rebuild or (collection.count() == 0):
        books = load_data()
        index_books(collection, books)
    return collection


def retrieved_context_snippets(results: List[Dict[str, Any]]) -> str:
    """
    Transformă rezultatele de la retriever într-un text compact care va fi dat modelului.
    """
    lines = []
    for rank, r in enumerate(results, start=1):
        title = r["metadata"]["title"]
        # din document extragem secțiunea rezumat
        doc = r["document"]
        lines.append(f"[{rank}] Titlu: {title}\n{doc}")
    return "\n---\n".join(lines)
