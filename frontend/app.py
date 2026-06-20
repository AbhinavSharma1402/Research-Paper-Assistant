import streamlit as st

from frontend.api_client import APIClient
from frontend.components import render_auth_forms, render_sidebar_controls, render_chat_interface, render_documents_overview


def initialize_state():
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "chats" not in st.session_state:
        st.session_state.chats = []
    if "documents" not in st.session_state:
        st.session_state.documents = []
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None


def main():
    st.set_page_config(page_title="Research Paper Assistant", layout="wide")
    initialize_state()

    client = APIClient()

    if st.session_state.token:
        client.set_token(st.session_state.token)
        try:
            st.session_state.user = client.get_me()
            if not st.session_state.chats:
                st.session_state.chats = client.list_chats()
            if not st.session_state.documents:
                st.session_state.documents = client.list_documents().get("documents", [])
            if not st.session_state.current_chat_id and st.session_state.chats:
                st.session_state.current_chat_id = st.session_state.chats[0]["id"]
        except Exception:
            st.warning("Session expired. Please login again.")
            st.session_state.token = None
            st.session_state.user = None

    if not st.session_state.token:
        render_auth_forms(client, st.session_state)
        return

    st.sidebar.title(f"Welcome, {st.session_state.user['email']}")
    uploaded_files = render_sidebar_controls(client, st.session_state)
    render_documents_overview(st.session_state)

    st.header("Research Chat Interface")
    render_chat_interface(client, st.session_state)


if __name__ == "__main__":
    main()
