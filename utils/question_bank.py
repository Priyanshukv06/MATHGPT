"""
utils/question_bank.py
CRUD operations for the personal question bank.
Uses Supabase if configured, falls back to local question_bank.json file.
"""
import os
import json
import random
from pathlib import Path

LOCAL_BANK_PATH = Path(__file__).parent.parent / "question_bank.json"

def _load_local() -> list:
    if LOCAL_BANK_PATH.exists():
        try:
            return json.loads(LOCAL_BANK_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def _save_local(questions: list) -> None:
    LOCAL_BANK_PATH.write_text(
        json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8"
    )

def _get_client():
    try:
        from utils.supabase_client import _get_client as get_sb
        return get_sb()
    except Exception:
        return None

def add_question(topic, difficulty, question, solution, source="", tags="") -> bool:
    entry = {
        "topic": topic.strip(), "difficulty": difficulty.strip(),
        "question": question.strip(), "solution": solution.strip(),
        "source": source.strip(), "tags": tags.strip(),
    }
    client = _get_client()
    if client:
        try:
            client.table("question_bank").insert(entry).execute()
        except Exception:
            pass
    import uuid
    existing = _load_local()
    entry["id"] = str(uuid.uuid4())
    existing.append(entry)
    _save_local(existing)
    return True

def get_questions(topic: str = "", difficulty: str = "") -> list:
    client = _get_client()
    if client:
        try:
            query = client.table("question_bank").select("*")
            if topic:      query = query.eq("topic", topic)
            if difficulty: query = query.eq("difficulty", difficulty)
            res = query.order("created_at", desc=True).execute()
            if res.data:
                return res.data
        except Exception:
            pass
    questions = _load_local()
    if topic:      questions = [q for q in questions if q.get("topic","").lower() == topic.lower()]
    if difficulty: questions = [q for q in questions if q.get("difficulty","").lower() == difficulty.lower()]
    return questions

def get_random_question(topic: str, difficulty: str) -> dict | None:
    pool = get_questions(topic, difficulty)
    if not pool:
        pool = get_questions(topic)
    return random.choice(pool) if pool else None

def delete_question(question_id: str) -> bool:
    client = _get_client()
    if client:
        try:
            client.table("question_bank").delete().eq("id", question_id).execute()
        except Exception:
            pass
    existing = _load_local()
    _save_local([q for q in existing if q.get("id") != question_id])
    return True

def get_all_questions() -> list:
    return get_questions()

def count_questions(topic: str = "", difficulty: str = "") -> int:
    return len(get_questions(topic, difficulty))