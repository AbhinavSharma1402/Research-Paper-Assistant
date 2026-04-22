import streamlit as st
import os

st.title("Research Paper Assistant")
st.write("Upload papers and ask questions")

os.makedirs("uploads", exist_ok=True)

uploaded = st.file_uploader("Upload PDF", type="pdf")

if uploaded:
    path = os.path.join("uploads", uploaded.name)

    with open(path, "wb") as f:
        f.write(uploaded.read())

    st.success("File saved successfully!")

from pdf_parser import extract_text

if uploaded:
    text = extract_text(path)
    st.text_area("Extracted Text", text[:3000])