
# Smart Librarian – AI with RAG + Tool Completion

AI chatbot (CLI) that recommends books based on user interests. **Note: The application and book summaries are in Romanian.**

---


## Project Structure

```
llm_integrations_project/
├── smart_librarian/         # Backend (Python, RAG, OpenAI, CLI)
│   ├── backend/             # API server (e.g., FastAPI)
│   ├── app_cli.py           # CLI chatbot
│   ├── rag.py, tools.py     # RAG logic, tool functions
│   └── vector_store.py      # ChromaDB integration
├── data/                    # Book summaries database
├── frontend/                # Frontend (Vite + React + TypeScript)
│   ├── src/                 # React source code
│   ├── index.html           # Entry point
│   └── vite.config.ts       # Vite config
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
└── README.md                # Project documentation
```

---


## What is included
- `data/book_summaries.json` (16 titles, in Romanian) + `data/book_summaries.md` for quick reading
- Python code:
   - `smart_librarian/tools.py` – includes `get_summary_by_title()` and the full summaries dictionary
   - `smart_librarian/vector_store.py` – ChromaDB initialization + OpenAI embeddings integration
   - `smart_librarian/rag.py` – RAG: indexing and retrieval, context formatting
   - `smart_librarian/app_cli.py` – CLI interface + OpenAI Chat integration + tool calling
- `requirements.txt`, `.env.example`, `README.md`


## Quickstart
1. Python 3.10+ (recommended).
2. Clone or download this project and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenAI key:
   ```bash
   # edit .env and set OPENAI_API_KEY
   ```
4. To run the backend API server:
   ```bash
   python -m uvicorn smart_librarian.backend.api_server:app --host 0.0.0.0 --port 8000 --reload
   ```
   This will start the FastAPI backend on http://localhost:8000.
---


## Frontend (React + Vite)

1. Go to the frontend folder:
   ```bash
   cd smart_librarian/frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Access the app at the shown address (usually http://localhost:5173).

> Make sure the backend (API) is running at http://localhost:8000, as set in the `VITE_API_BASE` variable in `.env`.

---


> On the first query, the Chroma collection is built (if empty). It persists in `./.chroma/`.


## How it works (short overview)
1. **Indexing**: `vector_store.index_books` loads `book_summaries.json` into Chroma; each document contains: *title, themes, short summary*.
2. **Embeddings**: uses `text-embedding-3-small` (OpenAI) for semantic (cosine) search.
3. **RAG**: `semantic_search()` returns the top *k* matches, which are packed as `BOOK_CONTEXT` and provided to the model.
4. **LLM + Tool**: the model is instructed to pick **one title** and call `get_summary_by_title(title)`. The final answer combines the recommendation + reasoning + **Full summary**.


## Example questions (in Romanian)
- „Vreau o carte despre **libertate** și **control social**.”
- „Ce-mi recomanzi dacă iubesc **poveștile fantastice**?”
- „Vreau o carte despre **prietenie** și **magie**.”
- „Ce este **1984**?”



## Useful notes
- You can set the model via the `CHAT_MODEL` env variable (e.g., `gpt-4o` or `gpt-4o-mini`).
- To force re-indexing, set `rebuild=True` in `run_chat_once` or delete the `./.chroma` folder.
- To extend the database, add titles to `data/book_summaries.json` (keep the same fields).
- The project uses OpenAI's Python library to interact with the API. The Chat Completions API allows the chatbot to generate answers and call tools/functions as needed. For semantic search, the `text-embedding-3-small` model converts book data and user queries into vectors, enabling the system to find the most relevant books based on meaning, not just keywords.




