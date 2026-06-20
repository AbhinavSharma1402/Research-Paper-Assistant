import os
from typing import List

import fitz
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import UploadFile, HTTPException

from backend.core.config import settings
from backend.core.logging import logger


def get_user_upload_dir(user_id: int) -> str:
    upload_path = os.path.join(settings.upload_dir, str(user_id))
    os.makedirs(upload_path, exist_ok=True)
    return upload_path


def save_uploaded_pdfs(user_id: int, files: List[UploadFile]) -> List[dict]:
    upload_dir = get_user_upload_dir(user_id)
    saved_files = []

    if len(files) > settings.max_upload_files:
        raise HTTPException(
            status_code=400,
            detail=f"Upload limit is {settings.max_upload_files} files at once.",
        )

    for upload in files:
        if upload.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

        file_path = os.path.join(upload_dir, upload.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(upload.file.read())

        saved_files.append({"filename": upload.filename, "path": file_path})
        logger.info("Saved PDF %s for user %s", upload.filename, user_id)

    return saved_files


def extract_text_from_pdf(file_path: str) -> str:
    document = fitz.open(file_path)
    text = []
    for page in document:
        text.append(page.get_text())
    return "\n".join(text)


def extract_page_count(file_path: str) -> int:
    document = fitz.open(file_path)
    return len(document)


def create_documents_from_pdf(file_path: str, filename: str) -> List[Document]:
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise HTTPException(status_code=422, detail=f"PDF {filename} contains no extractable text.")

    return [
        Document(
            page_content=text,
            metadata={"source": filename, "source_path": file_path},
        )
    ]


def chunk_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(documents)
