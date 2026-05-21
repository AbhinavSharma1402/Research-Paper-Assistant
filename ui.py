import streamlit as st


# -----------------------------
# PAGE CONFIG
# -----------------------------

def setup_page():

    st.set_page_config(
        page_title="Research Paper Assistant",
        layout="wide"
    )

    st.title("📚 Research Paper Assistant")


# -----------------------------
# SIDEBAR
# -----------------------------

def sidebar():

    st.sidebar.title("Options")

    uploaded_files = st.sidebar.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    new_chat = st.sidebar.button("➕ New Chat")

    return uploaded_files, new_chat


# -----------------------------
# DISPLAY CHAT
# -----------------------------

def display_messages(messages):

    for msg in messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
