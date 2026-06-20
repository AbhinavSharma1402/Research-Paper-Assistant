# Research Paper Assistant

Production-ready Research Paper Assistant with FastAPI backend, Streamlit frontend, JWT authentication, persistent chat memory, and retrieval-augmented generation (RAG).

## 🚀 What This Project Provides

* User registration, login, and JWT authentication
* Multi-document PDF upload (20+ PDFs supported)
* PDF parsing, intelligent chunking, embedding generation, and vector storage
* Cross-document question answering with context retrieval
* Persistent chat history and conversational memory per user
* FastAPI endpoints for auth, uploads, queries, chat history, and user management
* Streamlit frontend that communicates exclusively with the FastAPI backend
* Docker and docker-compose deployment for local development and production

## 📁 Architecture Overview

```
Research-Paper-Assistant/
├── backend/
│   ├── auth/                 # JWT auth helpers and schemas
│   ├── core/                 # configuration and logging
│   ├── db/                   # SQLAlchemy models, schemas, and CRUD
│   ├── routes/               # FastAPI endpoints
│   ├── services/             # PDF, vector store, RAG, and caching logic
│   └── main.py               # FastAPI application bootstrap
├── frontend/
│   ├── api_client.py         # HTTP client for Streamlit
│   ├── components.py         # Streamlit UI components
│   └── app.py                # Streamlit frontend
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md
```

## 🧠 High-Level Data Flow

1. User logs in and receives a JWT token
2. User uploads PDF files through the Streamlit UI
3. Backend saves PDFs, extracts text, and splits text into chunks
4. Embeddings are generated and stored in FAISS vector database
5. User asks a question via frontend
6. Backend performs similarity search and retrieves relevant context
7. LLM generates a response using retrieved document memory
8. Answer and sources are returned to the frontend and persisted in chat history

## 🔐 Authentication Flow

* `POST /api/auth/register` — create a new user
* `POST /api/auth/login` — authenticate and receive JWT
* `GET /api/users/me` — fetch authenticated user info

JWT tokens are signed using `JWT_SECRET_KEY` and validated on protected endpoints.

## 📦 API Endpoints

* `POST /api/auth/register` — register user
* `POST /api/auth/login` — login user
* `GET /api/users/me` — authenticated user profile
* `POST /api/documents/upload` — upload and index PDFs
* `GET /api/documents/` — list uploaded documents
* `POST /api/chats/` — create a chat session
* `GET /api/chats/` — list chat sessions
* `GET /api/chats/{chat_id}` — get chat metadata
* `GET /api/chats/{chat_id}/messages` — retrieve chat history
* `POST /api/chats/{chat_id}/query` — ask a question in a conversation

## 🗂️ Database Schema

* `users` — email, hashed password, timestamps
* `documents` — file metadata, storage path, page count, chunk count
* `chat_sessions` — per-user conversations
* `chat_messages` — user and assistant message logs
* `query_cache` — repeated question caching and sources

## 🧠 Conversational Memory

Every question and answer is saved to `chat_messages`, and follow-up queries are sent to the RAG chain with the full chat history for that session. This keeps context across turns and supports follow-up questions.

## ⚙️ RAG Pipeline

1. Extract text from PDFs using PyMuPDF
2. Chunk long documents with LangChain's `RecursiveCharacterTextSplitter`
3. Create embeddings with `sentence-transformers/all-MiniLM-L6-v2`
4. Store vectors in FAISS per user
5. Use `ConversationalRetrievalChain` to answer questions with retrieved context

## 🚀 Deployment

### Local Quickstart

1. Copy `.env.example` to `.env`
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
4. Start the Streamlit frontend:
   ```bash
   streamlit run frontend/app.py
   ```

### Docker Compose

Run the full system with one command:

```bash
docker-compose up --build
```

The backend will be available at `http://localhost:8000` and the frontend at `http://localhost:8501`.

## 📌 Notes for Interviews

* Backend is separated into modules for authentication, database, services, and routing.
* JWT authentication isolates user sessions and secures all protected APIs.
* Persistent storage is implemented with SQLAlchemy and a relational database schema.
* Chat memory is stored in the database, enabling follow-up questions in the same conversation.
* The vector database uses FAISS for high-performance semantic search.
* Docker Compose provides a reproducible containerized environment with Postgres, backend, and frontend.

## 🧪 Requirements

* Python 3.11+
* OpenAI API key stored in `.env`
* Docker and Docker Compose for containerized deployment

