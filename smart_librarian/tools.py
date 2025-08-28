
from __future__ import annotations

import json
import os
from typing import Dict
from dataclasses import dataclass

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "book_summaries.json")


@dataclass
class Book:
    title: str
    short_summary: str
    themes: list[str]
    full_summary: str


def _load_books() -> list[Book]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Book(**b) for b in raw]


BOOKS: list[Book] = _load_books()
BOOK_SUMMARIES_DICT: Dict[str, str] = {b.title: b.full_summary for b in BOOKS}


def get_summary_by_title(title: str) -> str:
    """
    Returnează rezumatul complet pentru un titlu exact.
    Dacă titlul nu există, returnează un mesaj clar.
    """
    summary = BOOK_SUMMARIES_DICT.get(title)
    if summary:
        return summary
    # Caută tolerant la caz (fallback)
    for key in BOOK_SUMMARIES_DICT.keys():
        if key.lower() == title.lower():
            return BOOK_SUMMARIES_DICT[key]
    return f"(Nu am găsit un rezumat pentru titlul: {title})"
