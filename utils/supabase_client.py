"""
utils/supabase_client.py
Supabase persistence — chat history + practice sessions + analytics.
"""
import os
from functools import lru_cache
from typing import Optional

try:
    from supabase import create_client, Client
    _SUPABASE_AVAILABLE = True
except ImportError:
    _SUPABASE_AVAILABLE = False


@lru_cache(maxsize=1)
def _get_client() -> Optional[object]:
    if not _SUPABASE_AVAILABLE:
        return None
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


def is_enabled() -> bool:
    return _get_client() is not None


# ── Chat history ──────────────────────────────────────────────────────

def save_message(session_id: str, role: str, content: str, model: str = "") -> None:
    client = _get_client()
    if not client:
        return
    try:
        client.table("chat_history").insert({
            "session_id": session_id,
            "role":       role,
            "content":    content,
            "model":      model,
        }).execute()
    except Exception:
        pass


def get_all_sessions() -> list:
    client = _get_client()
    if not client:
        return []
    try:
        res = (
            client.table("chat_history")
            .select("session_id, content, created_at")
            .eq("role", "user")
            .order("created_at", desc=True)
            .execute()
        )
        seen = {}
        for row in res.data or []:
            sid = row["session_id"]
            if sid not in seen:
                title = row["content"]
                seen[sid] = {
                    "session_id": sid,
                    "title":      title[:45] + "…" if len(title) > 45 else title,
                    "created_at": row["created_at"][:10],
                }
        return list(seen.values())
    except Exception:
        return []


def load_full_session(session_id: str) -> list:
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


# ── Practice sessions ─────────────────────────────────────────────────

def save_practice_attempt(
    session_id:  str,
    topic:       str,
    difficulty:  str,
    question:    str,
    user_answer: str,
    score:       int,
) -> None:
    client = _get_client()
    if not client:
        return
    try:
        client.table("practice_sessions").insert({
            "session_id":  session_id,
            "topic":       topic,
            "difficulty":  difficulty,
            "question":    question,
            "user_answer": user_answer,
            "score":       score,
        }).execute()
    except Exception:
        pass


# ── Analytics ─────────────────────────────────────────────────────────

def get_analytics() -> dict:
    client = _get_client()
    if not client:
        return {}
    try:
        return _get_analytics_fallback(client)
    except Exception:
        return {}


def _get_analytics_fallback(client) -> dict:
    """Compute analytics from raw table data — no stored procedures needed."""
    from collections import Counter, defaultdict
    try:
        out  = {}
        rows = client.table("chat_history").select("*").order("created_at").execute().data or []

        out["total_messages"] = len(rows)
        out["total_sessions"] = len({r["session_id"] for r in rows})

        # Messages per day (last 30 days)
        day_counts = Counter(r["created_at"][:10] for r in rows)
        out["messages_per_day"] = [
            {"day": d, "count": c}
            for d, c in sorted(day_counts.items())[-30:]
        ]

        # Model usage
        model_counts = Counter(r.get("model", "unknown") for r in rows)
        out["model_usage"] = [
            {"model": m, "count": c}
            for m, c in model_counts.most_common()
        ]

        # Role breakdown
        role_counts = Counter(r["role"] for r in rows)
        out["role_breakdown"] = [
            {"role": role, "count": c}
            for role, c in role_counts.items()
        ]

        # Recent sessions (last 10 unique)
        seen = {}
        for r in reversed(rows):
            sid = r["session_id"]
            if sid not in seen:
                seen[sid] = {"session_id": sid, "count": 0, "date": r["created_at"][:10]}
            seen[sid]["count"] += 1
        out["recent_sessions"] = [
            [v["session_id"], v["count"], v["date"]]
            for v in list(seen.values())[:10]
        ]

        # Practice stats
        try:
            prows = client.table("practice_sessions").select("*").execute().data or []
            out["practice_total"] = len(prows)
            scores = [r["score"] for r in prows if r.get("score") is not None]
            out["avg_practice_score"] = round(sum(scores) / len(scores), 1) if scores else 0

            topic_data = defaultdict(lambda: {"count": 0, "total_score": 0})
            for r in prows:
                t = r.get("topic", "Unknown")
                topic_data[t]["count"]       += 1
                topic_data[t]["total_score"] += r.get("score", 0)
            out["practice_by_topic"] = [
                {
                    "topic"    : t,
                    "count"    : v["count"],
                    "avg_score": round(v["total_score"] / v["count"], 1),
                }
                for t, v in topic_data.items()
            ]
        except Exception:
            out["practice_total"]     = 0
            out["avg_practice_score"] = 0
            out["practice_by_topic"]  = []

        return out
    except Exception:
        return {}