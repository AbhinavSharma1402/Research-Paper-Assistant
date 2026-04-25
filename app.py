import streamlit as st
import os
import fitz

from langchain_text_splitters import RecursiveCharacterTextSplitter

st.title("Research Paper Assistant")
st.write("Upload papers and ask questions")

os.makedirs("uploads", exist_ok=True)

uploaded_files = st.file_uploader(
    "Upload max 10 Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

documents = []

if uploaded_files:

    if len(uploaded_files) > 10:
        st.error("Maximum 10 PDFs allowed.")

    else:
        for uploaded in uploaded_files:

            pdf_bytes = uploaded.read()   # READ ONLY ONCE

            # Save PDF
            path = os.path.join("uploads", uploaded.name)
            with open(path, "wb") as f:
                f.write(pdf_bytes)

            # Open with PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

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

        st.success(f"{len(uploaded_files)} files uploaded successfully!")
        st.success(f"Text split into {len(documents)} chunks")

        st.text_area("Preview", str(documents[:3]), height=300)