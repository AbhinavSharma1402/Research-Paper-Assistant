from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class DocumentCreate(BaseModel):
    filename: str
    source_path: str


class DocumentRead(BaseModel):
    id: int
    filename: str
    source_path: str
    processed: bool
    page_count: int
    chunk_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime]

    class Config:
        orm_mode = True


class ChatMessageCreate(BaseModel):
    role: str
    content: str


class ChatMessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


class ChatSessionCreate(BaseModel):
    title: Optional[str] = "Research Chat"


class ChatSessionRead(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageRead] = []

    class Config:
        orm_mode = True


class QueryRequest(BaseModel):
    question: str
    chat_id: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    chat_id: int
    message_id: int


class DocumentListResponse(BaseModel):
    documents: List[DocumentRead]
