from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db import crud
from backend.utils.dependencies import get_db
from backend.db.schemas import (
    ChatMessageCreate,
    ChatMessageRead,
    ChatSessionCreate,
    ChatSessionRead,
    QueryRequest,
    QueryResponse,
)
from backend.services.cache_service import retrieve_cached_answer, save_cached_answer
from backend.services.rag_service import answer_question
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("/", response_model=ChatSessionRead)
def create_chat(chat_in: ChatSessionCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = crud.create_chat_session(db, current_user.id, chat_in)
    return session


@router.get("/", response_model=List[ChatSessionRead])
def list_chats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    chats = crud.list_chat_sessions(db, current_user.id)
    return chats


@router.get("/{chat_id}", response_model=ChatSessionRead)
def get_chat(chat_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    chat = crud.get_chat_session(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    return chat


@router.get("/{chat_id}/messages", response_model=List[ChatMessageRead])
def get_chat_messages(chat_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    chat = crud.get_chat_session(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")
    return crud.get_chat_history(db, chat_id)


@router.post("/{chat_id}/query", response_model=QueryResponse)
def query_chat(
    chat_id: int,
    request: QueryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = crud.get_chat_session(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")

    cached = retrieve_cached_answer(db, current_user.id, chat_id, request.question)
    if cached:
        assistant_message = crud.add_chat_message(
            db,
            chat_id,
            ChatMessageCreate(role="assistant", content=cached["answer"]),
        )
        return {
            "answer": cached["answer"],
            "sources": cached["sources"],
            "chat_id": chat_id,
            "message_id": assistant_message.id,
        }

    history = [
        (message.role, message.content)
        for message in crud.get_chat_history(db, chat_id)
    ]

    user_message = crud.add_chat_message(
        db,
        chat_id,
        ChatMessageCreate(role="user", content=request.question),
    )

    answer, sources = answer_question(current_user.id, request.question, history)
    assistant_message = crud.add_chat_message(
        db,
        chat_id,
        ChatMessageCreate(role="assistant", content=answer),
    )
    save_cached_answer(db, current_user.id, chat_id, request.question, answer, sources)

    return {
        "answer": answer,
        "sources": sources,
        "chat_id": chat_id,
        "message_id": assistant_message.id,
    }
