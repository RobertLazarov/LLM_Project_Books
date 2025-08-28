from __future__ import annotations

import os
from typing import Iterable, List, Dict, Any

import chromadb
from chromadb.api.models.Collection import Collection 
from chromadb.utils import embedding_functions


def get_chroma_collection(
    client=None,                     # păstrat pentru compatibilitate cu rag.py
    path: str = "./.chroma",
    name: str = "book_summaries",
    rebuild: bool = False,
) -> Collection:
    os.makedirs(path, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=path)

    if rebuild:
        try:
            chroma_client.delete_collection(name)
        except Exception:
            pass

    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    )

    collection = chroma_client.get_or_create_collection(
        name=name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def index_books(collection: Collection, books: Iterable[Dict[str, Any]]) -> None:
    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for i, b in enumerate(books):
        bid = f"book-{i+1:03d}-{b['title']}"
        doc = (
            f"Titlu: {b['title']}\n"
            f"Teme: {', '.join(b['themes'])}\n"
            f"Rezumat scurt: {b['short_summary']}\n"
        )
        meta = {
    "title": b["title"],
    # convertim lista în string; metadatele trebuie să fie scalare
    "themes": ", ".join(b["themes"]),
}
        ids.append(bid); documents.append(doc); metadatas.append(meta)

    if ids:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)


def semantic_search(collection: Collection, query: str, k: int = 3) -> list[dict]:
    res = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],  
    )

    docs = res.get("documents", [[]])[0] or []
    metas = res.get("metadatas", [[]])[0] or []
    ids = res.get("ids", [[]])[0] or []         
    dists = res.get("distances", [[]])[0] or []

    out: list[dict] = []
    for i in range(len(docs)):
        d = dists[i] if i < len(dists) else None
        out.append({
            "id": ids[i] if i < len(ids) else None,
            "document": docs[i],
            "metadata": metas[i] if i < len(metas) else {},
            "distance": d,
            "score": (1 - d) if isinstance(d, (int, float)) else None,
        })
    return out

