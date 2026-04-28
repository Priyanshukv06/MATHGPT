"""
Optional Supabase persistence layer.

Configure via st.secrets (Streamlit Cloud) or .env (local):
  SUPABASE_URL = "https://xxxx.supabase.co"
  SUPABASE_KEY = "your-anon-key"

If either value is missing the module degrades gracefully — the app
works without persistence; no errors are raised.

SQL schema (run once in Supabase SQL Editor):
─────────────────────────────────────────────
  CREATE TABLE IF NOT EXISTS chat_history (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT        NOT NULL,
    role       TEXT        NOT NULL CHECK (role IN ('user','assistant')),
    content    TEXT        NOT NULL,
    model      TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
  );
  CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);
"""
from __future__ import annotations
from datetime import datetime, timezone

import streamlit as st

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    try:
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if url and key:
            _client = create_client(url, key)
    except Exception:
        pass
    return _client


def is_enabled() -> bool:
    return _get_client() is not None


def save_message(
    session_id: str,
    role: str,
    content: str,
    model: str,
) -> None:
    client = _get_client()
    if not client:
        return
    try:
        client.table("chat_history").insert(
            {
                "session_id": session_id,
                "role"      : role,
                "content"   : content,
                "model"     : model,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()
    except Exception:
        pass   # never crash the app over persistence


def load_session(session_id: str) -> list[dict]:
    client = _get_client()
    if not client:
        return []
    try:
        res = (
            client.table("chat_history")
            .select("role, content")
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )
        return res.data or []
    except Exception:
        return []
