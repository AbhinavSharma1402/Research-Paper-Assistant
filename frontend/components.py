import streamlit as st


def render_auth_forms(client, session_state):
    st.title("Research Paper Assistant")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                data = client.login(email, password)
                session_state.token = data["access_token"]
                st.success("Logged in successfully.")
            except Exception as exc:
                st.error(f"Login failed: {exc}")

    with tab_register:
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register"):
            try:
                data = client.register(email, password)
                session_state.token = data["access_token"]
                st.success("Registration successful.")
            except Exception as exc:
                st.error(f"Registration failed: {exc}")


def render_sidebar_controls(client, session_state):
    st.sidebar.header("Upload & Chat")
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDFs (up to 20)",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_upload",
    )

    if uploaded_files and st.sidebar.button("Upload Documents"):
        try:
            client.upload_documents(uploaded_files)
            st.sidebar.success("Papers uploaded and indexed successfully.")
            session_state.documents = client.list_documents().get("documents", [])
        except Exception as exc:
            st.sidebar.error(f"Upload failed: {exc}")

    if st.sidebar.button("Refresh Chat List"):
        session_state.chats = client.list_chats()

    if st.sidebar.button("New Chat"):
        try:
            new_chat = client.create_chat("Research Assistant Chat")
            session_state.chats.append(new_chat)
            session_state.current_chat_id = new_chat["id"]
            st.sidebar.success("Created a new chat.")
        except Exception as exc:
            st.sidebar.error(f"Chat creation failed: {exc}")

    if session_state.chats:
        chat_options = {chat["title"]: chat["id"] for chat in session_state.chats}
        selected_title = st.sidebar.selectbox("Select chat", list(chat_options.keys()))
        session_state.current_chat_id = chat_options[selected_title]

    if st.sidebar.button("Logout"):
        session_state.token = None
        session_state.user = None
        session_state.chats = []
        session_state.documents = []
        session_state.current_chat_id = None
        st.experimental_rerun()

    return uploaded_files


def render_chat_interface(client, session_state):
    if not session_state.current_chat_id:
        st.info("Create a new chat or select an existing chat to begin.")
        return

    st.subheader("Chat history")
    history = client.get_chat_messages(session_state.current_chat_id)
    for message in history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Assistant:** {message['content']}")

    question = st.text_area("Ask your research question", key="question_text")
    if st.button("Send Question") and question.strip():
        try:
            response = client.query_chat(session_state.current_chat_id, question)
            st.success("Answer received from backend.")
            st.markdown(f"**Answer:** {response['answer']}")
            if response.get("sources"):
                st.markdown("**Source documents:**")
                for source in response["sources"]:
                    st.markdown(f"- {source}")
            session_state.message = response["answer"]
        except Exception as exc:
            st.error(f"Query failed: {exc}")


def render_documents_overview(session_state):
    if session_state.documents:
        st.sidebar.markdown("### Uploaded Documents")
        for document in session_state.documents:
            st.sidebar.markdown(f"- {document['filename']} ({document['chunk_count']} chunks)")
