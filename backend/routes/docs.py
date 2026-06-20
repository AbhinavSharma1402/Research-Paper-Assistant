from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.db import crud
from backend.db.schemas import DocumentRead, DocumentListResponse
from backend.utils.dependencies import get_current_user, get_db
from backend.services.pdf_service import (
    chunk_documents,
    create_documents_from_pdf,
    extract_page_count,
    save_uploaded_pdfs,
)
from backend.services.vector_service import append_documents
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentListResponse)
def upload_pdfs(
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved_items = save_uploaded_pdfs(current_user.id, files)
    processed_documents = []
    all_chunks = []

    for item in saved_items:
        document = crud.create_document(db, current_user.id, item["filename"], item["path"])
        documents = create_documents_from_pdf(item["path"], item["filename"])
        chunks = chunk_documents(documents)
        crud.update_document_processing(
            db,
            document_id=document.id,
            processed=True,
            page_count=extract_page_count(item["path"]),
            chunk_count=len(chunks),
        )
        all_chunks.extend(chunks)
        processed_documents.append(document)

    if all_chunks:
        append_documents(current_user.id, all_chunks)

    return {"documents": processed_documents}


@router.get("/", response_model=DocumentListResponse)
def list_documents(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    documents = crud.list_documents(db, current_user.id)
    return {"documents": documents}
