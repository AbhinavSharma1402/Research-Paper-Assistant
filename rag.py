import os
import fitz

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

from langchain_classic.chains.conversational_retrieval.base import ConversationalRetrievalChain


# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. "
        "Create a .env file and add your Gemini API key."
    )


# -----------------------------
# LOAD PDF TEXT
# -----------------------------

def extract_text_from_pdfs(pdf_files):

    documents = []

    os.makedirs("uploads", exist_ok=True)

    for pdf in pdf_files:

        pdf_path = os.path.join("uploads", pdf.name)

        with open(pdf_path, "wb") as f:
            f.write(pdf.read())

        doc = fitz.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()

        documents.append(
            Document(
                page_content=text,
                metadata={"source": pdf.name}
            )
        )

    return documents


# -----------------------------
# TEXT CHUNKING
# -----------------------------

def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    return chunks


# -----------------------------
# VECTOR STORE
# -----------------------------

def create_vectorstore(chunks):

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    vectorstore.save_local("vectorstore")

    return vectorstore


# -----------------------------
# LOAD VECTORSTORE
# -----------------------------

def load_vectorstore():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


# -----------------------------
# CREATE CHAT CHAIN
# -----------------------------

def create_chain(vectorstore):

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return chain