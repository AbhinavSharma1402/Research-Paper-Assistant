from typing import List, Tuple

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from backend.core.config import settings
from backend.services.vector_service import get_embeddings, load_vectorstore


def build_chat_chain(user_id: int):
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY must be set for the RAG pipeline.")

    vectorstore = load_vectorstore(user_id)
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=settings.openai_api_key,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": settings.query_top_k})
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
    )
    return chain


def parse_chain_output(result: dict) -> Tuple[str, List[str]]:
    answer = result.get("answer", "")
    docs = result.get("source_documents", [])
    sources = []
    for doc in docs:
        source = doc.metadata.get("source") or doc.metadata.get("source_path")
        if source and source not in sources:
            sources.append(source)
    return answer, sources


def answer_question(user_id: int, question: str, history: List[Tuple[str, str]]):
    chain = build_chat_chain(user_id)
    result = chain({"question": question, "chat_history": history})
    return parse_chain_output(result)
