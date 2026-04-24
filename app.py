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

from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

if uploaded_files and len(uploaded_files) <= 10:
    all_text = ""
    for uploaded in uploaded_files:
        path = os.path.join("uploads", uploaded.name)
        text = extract_text(path)
        all_text += text + "\n\n"
    
    # Split text into chunks
    chunks = splitter.split_text(all_text)
    st.success(f"Text split into {len(chunks)} chunks")
    
    st.text_area("Extracted Text", all_text[:3000])