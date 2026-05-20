import streamlit as st
import os
import fitz
from dotenv import load_dotenv

load_dotenv()

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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------- LOAD EMBEDDINGS ----------------
@st.cache_resource
def load_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# ---------------- LOAD TEXT SPLITTER ----------------
@st.cache_resource
def get_splitter():
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    return RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=80
    )


# ---------------- LOAD GEMINI MODEL ----------------
@st.cache_resource
def load_gemini():
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    return genai.GenerativeModel("models/gemini-2.5-flash")


# ---------------- CREATE DOCUMENTS ----------------
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


# ---------------- CREATE VECTORSTORE ----------------
def create_vectorstore(documents):
    from langchain_community.vectorstores import FAISS
    embeddings = load_embeddings()
    return FAISS.from_documents(documents, embeddings)


# ---------------- LOAD EXISTING VECTORSTORE ----------------
def load_existing_db():
    from langchain_community.vectorstores import FAISS
    embeddings = load_embeddings()
    return FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )


# ---------------- GENERATE ANSWER USING GEMINI ----------------
def generate_answer(question, docs, history):
    model = load_gemini()

    context = "\n\n".join([doc.page_content for doc in docs])

    conversation = ""
    for item in history[-3:]:
        conversation += f"""
        User: {item['question']}
        Assistant: {item['answer']}
        """

    prompt = f"""
    You are an intelligent research assistant.

    Use BOTH:
    1. Previous conversation history
    2. Retrieved research paper context

    to answer naturally and accurately.

    ---------------- Conversation History ----------------

    {conversation}

    ---------------- Research Context ----------------

    {context}

    ---------------- Current Question ----------------

    {question}

    ---------------- Instructions ----------------

    - Answer clearly and concisely
    - Use research context primarily
    - If answer is not in context, say:
      "I could not find this in the uploaded papers."
    - Maintain conversational continuity
    - Explain technical concepts simply

    Answer:
    """

    response = model.generate_content(prompt)

    return response.text


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

    question = st.chat_input(
        "Ask a question from papers..."
    )

    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

    # ---------------- DISPLAY OLD CHAT HISTORY ----------------
    for chat in st.session_state.chat_history:

        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):
            st.write(chat["answer"])

    # ---------------- NEW QUESTION ----------------
    if question:

        with st.chat_message("user"):
            st.write(question)

        with st.spinner("Thinking..."):

            docs = st.session_state.vectorstore.similarity_search(
                question,
                k=5
            )

            answer = generate_answer(
                question,
                docs,
                st.session_state.chat_history
            )

            with st.chat_message("assistant"):
                st.write(answer)

            st.session_state.chat_history.append({
                "question": question,
                "answer": answer
            })

            with st.expander("🔍 Source Context"):

                for i, doc in enumerate(docs, 1):

                    st.markdown(f"### Source {i}")

                    st.write(doc.page_content[:1200])

                    st.caption(
                        f"📄 {doc.metadata['source']}"
                    )