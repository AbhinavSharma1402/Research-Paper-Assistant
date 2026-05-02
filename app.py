import streamlit as st
import os
import fitz

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Research Paper Assistant", layout="wide")

st.title("Research Paper Assistant")
st.write("Upload papers, process once, then ask questions.")

# ---------------- FOLDERS ----------------
os.makedirs("uploads", exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)

# ---------------- SESSION STATE ----------------
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "processed" not in st.session_state:
    st.session_state.processed = False


# ---------------- FAST STARTUP ----------------
# Heavy imports moved inside functions

@st.cache_resource
def load_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


@st.cache_resource
def get_splitter():
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    return RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=80
    )


def create_documents(files):
    from langchain_core.documents import Document

    splitter = get_splitter()
    docs = []

    for uploaded in files:
        try:
            pdf_bytes = uploaded.getvalue()
            pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

            text = ""
            for page in pdf:
                text += page.get_text("text")

            pdf.close()

            chunks = splitter.split_text(text)

            for chunk in chunks:
                docs.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": uploaded.name}
                    )
                )

        except Exception as e:
            st.warning(f"Error in {uploaded.name}: {e}")

    return docs


def create_vectorstore(documents):
    from langchain_community.vectorstores import FAISS

    embeddings = load_embeddings()

    return FAISS.from_documents(documents, embeddings)


def load_existing_db():
    from langchain_community.vectorstores import FAISS

    embeddings = load_embeddings()

    return FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )


# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload up to 10 PDFs",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} files selected.")

# ---------------- PROCESS BUTTON ----------------
if uploaded_files and st.button("Process Papers"):

    with st.spinner("Processing PDFs..."):

        docs = create_documents(uploaded_files)

        if docs:
            db = create_vectorstore(docs)

            db.save_local("vectorstore")

            st.session_state.vectorstore = db
            st.session_state.processed = True

            st.success(f"Done! {len(docs)} chunks indexed.")

        else:
            st.error("No readable text found.")

# ---------------- LOAD EXISTING DATABASE ----------------
if st.button("Load Existing Database"):

    with st.spinner("Loading database..."):

        try:
            db = load_existing_db()

            st.session_state.vectorstore = db
            st.session_state.processed = True

            st.success("Database loaded successfully!")

        except Exception as e:
            st.error(e)

# ---------------- ASK QUESTIONS ----------------
if st.session_state.processed:

    question = st.text_input("Ask a question from papers")

    if question and st.button("Search"):

        with st.spinner("Searching..."):

            docs = st.session_state.vectorstore.similarity_search(
                question,
                k=3
            )

            for i, doc in enumerate(docs, 1):
                st.markdown(f"### Result {i}")
                st.write(doc.page_content[:1500])
                st.caption(doc.metadata["source"])