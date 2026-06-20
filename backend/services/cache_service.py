from typing import Optional

from sqlalchemy.orm import Session

from backend.db import crud


def retrieve_cached_answer(db: Session, user_id: int, chat_id: int, question_text: str) -> Optional[dict]:
    cached = crud.get_cached_answer(db, user_id, chat_id, question_text)
    if not cached:
        return None
    return {
        "answer": cached.answer_text,
        "sources": [src for src in (cached.sources or "").split("||") if src],
    }


def save_cached_answer(db: Session, user_id: int, chat_id: int, question_text: str, answer_text: str, sources: list[str]):
    sources_string = "||".join(sources)
    return crud.cache_answer(db, user_id, chat_id, question_text, answer_text, sources_string)
