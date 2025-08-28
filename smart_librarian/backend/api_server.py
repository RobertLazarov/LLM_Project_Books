from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

# Refolosim logica din CLI
from smart_librarian.app_cli import health_check, run_chat_once
from smart_librarian.rag import build_or_load_store

load_dotenv(override=True)

app = FastAPI(title="Smart Librarian API", version="1.0.0")

# CORS pentru front-end local
FRONTEND_ORIGINS = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:3000", "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    k: int = Field(3, ge=1, le=8)
    rebuild: bool = Field(False)

class ChatResponse(BaseModel):
    answer: str

@app.get("/api/health")
def api_health() -> dict:
    ok = health_check()
    return {"ok": ok}

@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest) -> ChatResponse:
    try:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            organization=os.getenv("OPENAI_ORG_ID") or None
        )
        # Încarcă/creează vector-store
        _ = build_or_load_store(client=client, rebuild=req.rebuild)
        answer = run_chat_once(client=client, question=req.question, rebuild_store=False, k=req.k)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
