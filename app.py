import streamlit as st
import os
import fitz

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

st.title("Research Paper Assistant")

os.makedirs("uploads", exist_ok=True)

@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

uploaded_files = st.file_uploader(
    "Upload max 10 PDFs",
    type="pdf",
    accept_multiple_files=True
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

documents = []

if uploaded_files:

    if len(uploaded_files) > 10:
        st.error("Maximum 10 PDFs allowed")

    else:
        for uploaded in uploaded_files:

            pdf_bytes = uploaded.getvalue()

            path = os.path.join("uploads", uploaded.name)

            with open(path, "wb") as f:
                f.write(pdf_bytes)

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

            if text.strip():

                chunks = splitter.split_text(text)

                for chunk in chunks:
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={"source": uploaded.name}
                        )
                    )

if documents:

    if "vectorstore" not in st.session_state:

        embeddings = load_embeddings()

        st.session_state.vectorstore = FAISS.from_documents(
            documents,
            embeddings
        )

        st.session_state.vectorstore.save_local("vectorstore")

        st.success("Vector Store Ready!")