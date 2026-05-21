import os
import streamlit as st

from rag import (
    extract_text_from_pdfs,
    split_documents,
    create_vectorstore,
    load_vectorstore,
    create_chain
)

from memory import (
    create_chat,
    load_chat,
    save_message
)

from ui import (
    setup_page,
    sidebar,
    display_messages
)

# -----------------------------
# SETUP
# -----------------------------

os.makedirs("uploads", exist_ok=True)

setup_page()

# -----------------------------
# SESSION STATE
# -----------------------------

if "chat_id" not in st.session_state:
    st.session_state.chat_id = create_chat()

if "messages" not in st.session_state:
    st.session_state.messages = load_chat(
        st.session_state.chat_id
    )

# -----------------------------
# SIDEBAR
# -----------------------------

uploaded_files, new_chat = sidebar()

# -----------------------------
# NEW CHAT
# -----------------------------

if new_chat:

    st.session_state.chat_id = create_chat()

    st.session_state.messages = []

    st.rerun()

# -----------------------------
# PROCESS PDFs
# -----------------------------

if uploaded_files:

    with st.spinner("Processing PDFs..."):

        docs = extract_text_from_pdfs(uploaded_files)

        chunks = split_documents(docs)

        vectorstore = create_vectorstore(chunks)

        chain = create_chain(vectorstore)

        st.session_state.chain = chain

    st.success("PDFs processed successfully!")

# -----------------------------
# DISPLAY CHAT
# -----------------------------

display_messages(st.session_state.messages)

# -----------------------------
# USER INPUT
# -----------------------------

prompt = st.chat_input("Ask your research question...")

if prompt:

    # show user
    with st.chat_message("user"):
        st.markdown(prompt)

    save_message(
        st.session_state.chat_id,
        "user",
        prompt
    )

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # generate answer
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            result = st.session_state.chain.invoke({
                "question": prompt,
                "chat_history": [
                    (
                        m["role"],
                        m["content"]
                    )
                    for m in st.session_state.messages
                ]
            })

            answer = result["answer"]

            st.markdown(answer)

    # save assistant message
    save_message(
        st.session_state.chat_id,
        "assistant",
        answer
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })