import os
from typing import List

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

from backend.core.config import settings
from backend.core.logging import logger


def get_vector_store_dir(user_id: int) -> str:
    vector_path = os.path.join(settings.vector_store_root, str(user_id))
    os.makedirs(vector_path, exist_ok=True)
    return vector_path


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def load_vectorstore(user_id: int) -> FAISS:
    vector_dir = get_vector_store_dir(user_id)
    embeddings = get_embeddings()
    if not os.path.isdir(vector_dir) or not os.listdir(vector_dir):
        raise FileNotFoundError("Vector store has not been created for this user yet.")
    return FAISS.load_local(vector_dir, embeddings)


def build_vectorstore(user_id: int, documents: List[Document]) -> FAISS:
    vector_dir = get_vector_store_dir(user_id)
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(vector_dir)
    logger.info("Created vectorstore for user %s with %s chunks", user_id, len(documents))
    return vectorstore


def append_documents(user_id: int, documents: List[Document]) -> FAISS:
    vector_dir = get_vector_store_dir(user_id)
    embeddings = get_embeddings()
    if os.path.isdir(vector_dir) and os.listdir(vector_dir):
        vectorstore = FAISS.load_local(vector_dir, embeddings)
        vectorstore.add_documents(documents)
    else:
        vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(vector_dir)
    logger.info("Appended %s chunks to vectorstore for user %s", len(documents), user_id)
    return vectorstore


def search_documents(user_id: int, query: str, k: int = 5) -> List[Document]:
    vectorstore = load_vectorstore(user_id)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.get_relevant_documents(query)
