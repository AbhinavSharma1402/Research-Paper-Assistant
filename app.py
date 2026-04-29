import streamlit as st
import os
import fitz

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Research Paper Assistant", layout="wide")

st.title("Research Paper Assistant")
st.write("Upload papers, process once, then ask questions.")

# ---------------- FOLDERS ----------------
os.makedirs("uploads", exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)

# ---------------- CACHE MODEL ----------------
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

# ---------------- TEXT SPLITTER ----------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=150
)

# ---------------- SESSION STATE ----------------
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "processed" not in st.session_state:
    st.session_state.processed = False

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload up to 10 PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- SAVE FILES ONLY ----------------
if uploaded_files:

    if len(uploaded_files) > 10:
        st.error("Maximum 10 PDFs allowed.")

    else:
        for uploaded in uploaded_files:
            path = os.path.join("uploads", uploaded.name)

            with open(path, "wb") as f:
                f.write(uploaded.getvalue())

        st.success(f"{len(uploaded_files)} PDFs uploaded successfully!")

# ---------------- PROCESS BUTTON ----------------
if uploaded_files and st.button("Process Papers"):

    with st.spinner("Reading PDFs and creating vector database..."):

        documents = []

        for uploaded in uploaded_files:

            pdf_bytes = uploaded.getvalue()

            try:
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

            except Exception as e:
                st.warning(f"Could not process {uploaded.name}")

        if documents:

            embeddings = load_embeddings()

            vectorstore = FAISS.from_documents(
                documents,
                embeddings
            )

            vectorstore.save_local("vectorstore")

            st.session_state.vectorstore = vectorstore
            st.session_state.processed = True

            st.success(f"Done! {len(documents)} chunks indexed.")

        else:
            st.error("No readable text found in PDFs.")

# ---------------- LOAD EXISTING DB ----------------
if (
    st.session_state.vectorstore is None
    and os.path.exists("vectorstore/index.faiss")
):
    try:
        embeddings = load_embeddings()

        st.session_state.vectorstore = FAISS.load_local(
            "vectorstore",
            embeddings,
            allow_dangerous_deserialization=True
        )

        st.session_state.processed = True

    except:
        pass

