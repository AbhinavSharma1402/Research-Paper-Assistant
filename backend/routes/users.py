from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db import crud
from backend.utils.dependencies import get_db
from backend.db.schemas import UserRead, DocumentListResponse
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user=Depends(get_current_user)):
    return current_user


@router.get("/me/documents", response_model=DocumentListResponse)
def read_current_user_documents(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    documents = crud.list_documents(db, current_user.id)
    return {"documents": documents}
