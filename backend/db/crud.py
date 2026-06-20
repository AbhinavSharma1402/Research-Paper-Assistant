from datetime import datetime
from hashlib import sha256
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.auth.security import create_password_hash, verify_password
from backend.db import models
from backend.db.schemas import UserCreate, ChatSessionCreate, ChatMessageCreate


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: UserCreate) -> models.User:
    hashed_password = create_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_document(db: Session, user_id: int, filename: str, source_path: str) -> models.Document:
    document = models.Document(user_id=user_id, filename=filename, source_path=source_path)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document_processing(db: Session, document_id: int, processed: bool, page_count: int, chunk_count: int):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if document:
        document.processed = processed
        document.page_count = page_count
        document.chunk_count = chunk_count
        document.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(document)
    return document


def list_documents(db: Session, user_id: int) -> List[models.Document]:
    return db.query(models.Document).filter(models.Document.user_id == user_id).order_by(models.Document.uploaded_at.desc()).all()


def create_chat_session(db: Session, user_id: int, chat_in: ChatSessionCreate) -> models.ChatSession:
    session = models.ChatSession(user_id=user_id, title=chat_in.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_chat_sessions(db: Session, user_id: int) -> List[models.ChatSession]:
    return db.query(models.ChatSession).filter(models.ChatSession.user_id == user_id).order_by(models.ChatSession.updated_at.desc()).all()


def get_chat_session(db: Session, chat_id: int, user_id: int) -> Optional[models.ChatSession]:
    return db.query(models.ChatSession).filter(models.ChatSession.id == chat_id, models.ChatSession.user_id == user_id).first()


def add_chat_message(db: Session, chat_id: int, message_in: ChatMessageCreate) -> models.ChatMessage:
    message = models.ChatMessage(chat_id=chat_id, role=message_in.role, content=message_in.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_chat_history(db: Session, chat_id: int) -> List[models.ChatMessage]:
    return db.query(models.ChatMessage).filter(models.ChatMessage.chat_id == chat_id).order_by(models.ChatMessage.created_at.asc()).all()


def cache_answer(db: Session, user_id: int, chat_id: int, question_text: str, answer_text: str, sources: str) -> models.QueryCache:
    query_hash = sha256(f"{user_id}:{chat_id}:{question_text}".encode("utf-8")).hexdigest()
    cached = db.query(models.QueryCache).filter(models.QueryCache.user_id == user_id, models.QueryCache.question_hash == query_hash).first()
    if cached:
        cached.answer_text = answer_text
        cached.sources = sources
        cached.updated_at = datetime.utcnow()
    else:
        cached = models.QueryCache(
            user_id=user_id,
            chat_id=chat_id,
            question_hash=query_hash,
            question_text=question_text,
            answer_text=answer_text,
            sources=sources,
        )
        db.add(cached)
    db.commit()
    db.refresh(cached)
    return cached


def get_cached_answer(db: Session, user_id: int, chat_id: int, question_text: str) -> Optional[models.QueryCache]:
    query_hash = sha256(f"{user_id}:{chat_id}:{question_text}".encode("utf-8")).hexdigest()
    return db.query(models.QueryCache).filter(models.QueryCache.user_id == user_id, models.QueryCache.chat_id == chat_id, models.QueryCache.question_hash == query_hash).first()
