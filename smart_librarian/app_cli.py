from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from smart_librarian.rag import build_or_load_store, semantic_search, retrieved_context_snippets
from smart_librarian.tools import get_summary_by_title


SYSTEM_PROMPT = """Ești Smart Librarian, un bibliotecar AI.
Primești întrebări de la utilizatori despre ce cărți ar trebui să citească.
Ai acces la un "BOOK_CONTEXT" (rezultatele unui retriever semantic) și la un tool numit get_summary_by_title(title).
Sarcina ta:
1) Alege o singură carte din BOOK_CONTEXT care se potrivește cel mai bine întrebării.
2) Explică pe scurt de ce ai ales acea carte (2–4 propoziții).
3) Apelează tool-ul get_summary_by_title EXACT cu titlul ales (o singură chemare).
4) În răspunsul final, afișează titlul recomandat, motivarea, apoi secțiunea „Rezumat complet” cu conținutul returnat de tool.
IMPORTANT:
- Dacă BOOK_CONTEXT nu conține o potrivire bună, alege totuși cea mai apropiată și explică ipoteza.
- Nu inventa titluri care nu apar în BOOK_CONTEXT.
- Chemarea către tool trebuie să aibă exact parametrul: title=<titlul selectat>.
- Scrie în limba română.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_by_title",
            "description": "Returnează rezumatul complet pentru un titlu exact de carte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Titlul exact al cărții recomandate."}
                },
                "required": ["title"],
                "additionalProperties": False,
            },
        },
    }
]


def mask_key(k: Optional[str]) -> str:
    if not k:
        return "(none)"
    if len(k) <= 12:
        return k[:4] + "..." + k[-2:]
    return k[:6] + "..." + k[-4:]


def health_check() -> bool:
    """
    Verifică:
      - dacă OPENAI_API_KEY e încărcată
      - dacă embeddings funcționează (text-embedding-3-small)
      - dacă un chat minim funcționează (gpt-4o-mini, by default)
    Returnează True dacă e OK, altfel False și tipărește mesaje clare.
    """
    ok = True
    key = os.getenv("OPENAI_API_KEY")
    print(f"[health] OPENAI_API_KEY: {mask_key(key)}")

    if not key:
        print("[health][ERROR] OPENAI_API_KEY lipsește. Setează în .env sau în mediu.")
        return False

    try:
        client = OpenAI(api_key=key, organization=os.getenv("OPENAI_ORG_ID") or None)
        # 1) embeddings smoke test
        emb_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        e = client.embeddings.create(model=emb_model, input=["ping"])
        dim = len(e.data[0].embedding)
        print(f"[health] embeddings OK (model={emb_model}, dim={dim})")
    except Exception as ex:
        print(f"[health][ERROR] embeddings failed: {ex}")
        ok = False

    try:
        chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        r = client.chat.completions.create(
            model=chat_model,
            messages=[{"role": "system", "content": "ping"}, {"role": "user", "content": "ping"}],
            temperature=0.0,
        )
        print(f"[health] chat OK (model={chat_model})")
    except Exception as ex:
        print(f"[health][ERROR] chat failed: {ex}")
        ok = False

    if ok:
        print("[health] All good ✅")
    else:
        print("[health] Probleme detectate ❌ — vezi mesajele de mai sus.")
    return ok


def run_chat_once(client: OpenAI, question: str, rebuild_store: bool = False, k: int = 3, model: str = None) -> str:
    model = model or os.getenv("CHAT_MODEL", "gpt-4o-mini")
    collection = build_or_load_store(client=client, rebuild=rebuild_store)
    results = semantic_search(collection, question, k=k)
    context = retrieved_context_snippets(results)

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Întrebare: {question}\n\nBOOK_CONTEXT:\n{context}",
        },
    ]

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.2,
    )

    msg = resp.choices[0].message
    tool_calls = getattr(msg, "tool_calls", None)

    if tool_calls:
        followup_messages = messages + [msg]
        for tc in tool_calls:
            if tc.function.name == "get_summary_by_title":
                args = json.loads(tc.function.arguments or "{}")
                title = args.get("title")
                summary = get_summary_by_title(title)
                followup_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": "get_summary_by_title",
                        "content": summary,
                    }
                )

        final = client.chat.completions.create(
            model=model,
            messages=followup_messages,
            temperature=0.2,
        )
        return final.choices[0].message.content or ""
    else:
        content = msg.content or ""
        title = results[0]["metadata"]["title"] if results else None
        summary = get_summary_by_title(title) if title else "(Nu există rezultate)"
        return f"{content}\n\n**Rezumat complet**\n{summary}"


def interactive_loop() -> None:
    # IMPORTANT: suprascrie variabilele din mediu cu cele din .env (dacă există)
    load_dotenv(override=True)

    # Health check la pornire sau dacă treci --health ca prim argument
    if len(sys.argv) > 1 and sys.argv[1] == "--health":
        _ = health_check()
        return
    else:
        # rulează health check automat o singură dată; dacă pică, afișăm mesaje dar lăsăm userul să încerce oricum
        health_check()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), organization=os.getenv("OPENAI_ORG_ID") or None)
    print("=== Smart Librarian (CLI) ===")
    print("Exemple:")
    print("- Vreau o carte despre libertate și control social.")
    print("- Ce-mi recomanzi dacă iubesc poveștile fantastice?")
    print("- Vreau ceva despre prietenie și magie.")
    print("- Ce este 1984?")
    print("Tastează 'exit' pentru a ieși.\n")

    while True:
        try:
            q = input("Întrebarea ta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLa revedere!")
            break
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            print("La revedere!")
            break
        try:
            answer = run_chat_once(client, q, rebuild_store=False)
            print("\n--- Răspuns ---")
            print(answer)
            print("---------------\n")
        except Exception as e:
            print(f"Eroare: {e}", file=sys.stderr)


if __name__ == "__main__":
    interactive_loop()
