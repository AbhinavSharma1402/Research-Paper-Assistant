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

# ---------------- OPTIMIZED TEXT SPLITTER ----------------
# Reduced chunk size for faster processing
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Reduced from 1500
    chunk_overlap=50  # Reduced from 150
)

# ---------------- SESSION STATE ----------------
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "processed" not in st.session_state:
    st.session_state.processed = False

if "embeddings_loaded" not in st.session_state:
    st.session_state.embeddings_loaded = False

# ---------------- LAZY LOAD EMBEDDINGS ----------------
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

# ---------------- FAST TEXT EXTRACTION ----------------
def extract_text_fast(pdf_bytes):
    """Extract text using faster method"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    doc.close()
    return text

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
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("Reading PDFs and creating vector database..."):
        documents = []
        total_files = len(uploaded_files)
        
        for idx, uploaded in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded.name} ({idx+1}/{total_files})")
            progress_bar.progress((idx) / total_files)
            
            pdf_bytes = uploaded.getvalue()
            try:
                text = extract_text_fast(pdf_bytes)
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
                st.warning(f"Could not process {uploaded.name}: {e}")
        
        if documents:
            status_text.text("Creating vector database...")
            progress_bar.progress(80 / 100)
            
            embeddings = load_embeddings()
            
            vectorstore = FAISS.from_documents(
                documents,
                embeddings
            )
            
            vectorstore.save_local("vectorstore")
            
            st.session_state.vectorstore = vectorstore
            st.session_state.processed = True
            st.session_state.embeddings_loaded = True
            
            progress_bar.progress(100)
            status_text.text("Done!")
            st.success(f"Done! {len(documents)} chunks indexed.")
        else:
            st.error("No readable text found in PDFs.")

# ---------------- LAZY LOAD EXISTING DB ----------------
# Only load if not already loaded and file exists
# if (
#     st.session_state.vectorstore is None
#     and os.path.exists("vectorstore/index.faiss")
# ):
#     with st.spinner("Loading existing database..."):
#         try:
#             embeddings = load_embeddings()
#             st.session_state.vectorstore = FAISS.load_local(
#                 "vectorstore",
#                 embeddings,
#                 allow_dangerous_deserialization=True
#             )
#             st.session_state.processed = True
#             st.session_state.embeddings_loaded = True
#         except Exception as e:
#             st.error(f"Failed to load existing database: {e}")