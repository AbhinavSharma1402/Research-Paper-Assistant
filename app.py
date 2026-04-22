import streamlit as st

st.title("Research Paper Assistant")
st.write("Upload papers and ask questions")
uploaded = st.file_uploader("Upload PDF", type="pdf")

if uploaded:
    with open("uploads/temp.pdf", "wb") as f:
        f.write(uploaded.read())