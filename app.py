import streamlit as st
import os

st.title("Research Paper Assistant")
st.write("Upload papers and ask questions")

os.makedirs("uploads", exist_ok=True)

uploaded_files = st.file_uploader(
    "Upload max 10 Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 10:
        st.error("Maximum 10 PDFs allowed.")
    else:
        for uploaded in uploaded_files:
            path = os.path.join("uploads", uploaded.name)
            with open(path, "wb") as f:
                f.write(uploaded.read())
        st.success(f"{len(uploaded_files)} files uploaded successfully!")

from pdf_parser import extract_text
import fitz  # PyMuPDF

from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

documents = []

if uploaded_files and len(uploaded_files) <= 10:
    for uploaded in uploaded_files:
        # Open PDF with PyMuPDF
        doc = fitz.open(stream=uploaded.read(), filetype="pdf")

        text = ""
        for page in doc:
            text += page.get_text()

        doc.close()

        chunks = splitter.split_text(text)

        for chunk in chunks:
            documents.append({
                "text": chunk,
                "source": uploaded.name
            })

    st.success(f"Text split into {len(documents)} chunks")
    st.text_area("Documents", str(documents[:3])[:3000])