import streamlit as st

st.title("Research Paper Assistant")
st.write("Upload papers and ask questions")
uploaded = st.file_uploader("Upload PDF", type="pdf")

if uploaded:
    with open("uploads/temp.pdf", "wb") as f:
        f.write(uploaded.read())

from pdf_parser import extract_text

if uploaded:
    text = extract_text("uploads/temp.pdf")
    st.text_area("Extracted Text", text[:3000])