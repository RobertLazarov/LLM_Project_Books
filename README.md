# Smart Librarian – AI cu RAG + Tool Completion

Construiește un chatbot AI (CLI) care recomandă cărți pe baza intereselor utilizatorului folosind:
- **OpenAI GPT** (Chat Completions API cu *function calling*)
- **RAG** cu **ChromaDB**
- **Tool** `get_summary_by_title(title: str)` pentru a afișa *rezumatul complet* după recomandare

## Ce este livrat
- `data/book_summaries.json` (16 titluri, în RO) + `data/book_summaries.md` pentru citire rapidă
- Cod Python:
  - `smart_librarian/tools.py` – include `get_summary_by_title()` și dict-ul de rezumate complete
  - `smart_librarian/vector_store.py` – inițializare Chroma + integrare embeddings OpenAI
  - `smart_librarian/rag.py` – RAG: indexare și recuperare, formatarea contextului
  - `smart_librarian/app_cli.py` – interfața CLI + integrarea cu OpenAI Chat + tool calling
- `requirements.txt`, `.env.example`, `README.md`

## Instalare rapidă
1. Python 3.10+ (recomandat).
2. Clonează sau descarcă acest proiect și instalează dependențele:
   ```bash
   pip install -r requirements.txt
   ```
3. Configurează cheia OpenAI:
   ```bash
   cp .env.example .env
   # editează .env și setează OPENAI_API_KEY
   ```
4. Rulează CLI:
   ```bash
   python -m smart_librarian.app_cli
   ```

> La prima interogare, colecția Chroma se construiește (dacă e goală). Persistă în `./.chroma/`.

## Cum funcționează (pe scurt)
1. **Indexare**: `vector_store.index_books` încarcă `book_summaries.json` în Chroma; fiecare document conține: *titlu, teme, rezumat scurt*.
2. **Embeddings**: folosim `text-embedding-3-small` (OpenAI) pentru căutare semantică (cosine). 
3. **RAG**: `semantic_search()` returnează primele *k* potriviri, care sunt ambalate drept `BOOK_CONTEXT` și oferite modelului.
4. **LLM + Tool**: modelul primește instrucțiuni să aleagă **un singur titlu** și să apeleze `get_summary_by_title(title)`. Răspunsul final combină recomandarea + motivarea + **Rezumat complet**.

## Exemple de întrebări
- „Vreau o carte despre **libertate** și **control social**.”
- „Ce-mi recomanzi dacă iubesc **poveștile fantastice**?”
- „Vreau o carte despre **prietenie** și **magie**.”
- „Ce este **1984**?”

## Note utile
- Poți seta modelul prin env `CHAT_MODEL` (ex: `gpt-4o` sau `gpt-4o-mini`).
- Dacă vrei să re-indexezi forțat, modifică `rebuild=True` în `run_chat_once` sau șterge folderul `./.chroma`.
- Pentru a extinde baza de date, adaugă titluri în `data/book_summaries.json` (menține câmpurile).

## Referințe oficiale (OpenAI)
- **Librăria Python** și exemple `OpenAI()` + Chat Completions: vezi README-ul oficial al pachetului `openai` pe GitHub. 
- **Embeddings** `text-embedding-3-small`: vezi documentația oficială a modelului și endpointul `embeddings.create`.
- **Function calling (tools)** cu Chat Completions: vezi ghidul oficial.

