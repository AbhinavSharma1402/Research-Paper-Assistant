# Research Paper Assistant

A Streamlit-based application that allows users to upload multiple research papers (PDFs), extract text, create embeddings, and ask questions across the papers using Retrieval-Augmented Generation (RAG).

## 🚀 Current Progress

### ✅ Step 1: Multi-PDF Upload Interface

Users can upload up to 10 PDF research papers through a clean Streamlit UI.

**Features:**

* Multiple file upload support
* PDF-only validation
* Maximum 10 files allowed
* Success/error messages in the UI

### ✅ Step 2: PDF Text Extraction + Chunking

Uploaded PDFs are processed and converted into text using PyMuPDF.
The extracted text is then split into smaller chunks for embedding generation.

**Libraries Used:**

* `PyMuPDF (fitz)` for PDF parsing
* `RecursiveCharacterTextSplitter` from LangChain for chunking

**Chunk Settings:**

* `chunk_size = 700`
* `chunk_overlap = 80`

**Stored Output Format:**
Each chunk is stored as a LangChain Document with source metadata:

```python
{
  "page_content": "chunk content...",
  "metadata": {"source": "paper_name.pdf"}
}
```

### ✅ Step 3: Vector Embeddings & FAISS Storage

Processed chunks are converted into embeddings using HuggingFace's sentence-transformers model and stored in a FAISS vectorstore for fast similarity search.

**Embedding Model:**
* `sentence-transformers/all-MiniLM-L6-v2`

**Storage:**
* Vectorstore saved locally in `vectorstore/` folder
* Persists across sessions

### ✅ Step 4: Semantic Search & Question Answering

Users can load the vectorstore and ask questions about the papers. The app retrieves the top 3 most relevant chunks and displays them.

**Features:**
* Load existing vectorstore or process new papers
* Ask questions via text input
* Display top 3 relevant results with source attribution
* Full chunk content preview (first 1500 characters)

## 📁 Project Structure

```text
Research-Paper-Assistant/
├── app.py                    # Main Streamlit application
├── pdf_parser.py             # PDF parsing utilities
├── rag.py                    # RAG pipeline utilities
├── utils.py                  # Helper utilities
├── uploads/                  # Temporary storage for uploaded PDFs
├── vectorstore/              # FAISS vectorstore persistence
│   └── index.faiss
├── README.md
└── requirements.txt
```

## ▶️ Run the App

```bash
streamlit run app.py
```

The app will start at `http://localhost:8501`

## 🎯 UI Components

| Component | Description |
|-----------|-------------|
| **File Uploader** | Upload up to 10 PDF research papers |
| **Process Papers** | Button to extract text, chunk, embed, and index papers |
| **Load Existing Database** | Button to load a previously processed vectorstore |
| **Question Input** | Text field to ask questions about the papers |
| **Search Button** | Triggers semantic search across indexed papers |
| **Results Display** | Shows top 3 most relevant chunks with source attribution |

## 🧪 Current Workflow

**Option 1: Process New Papers**
1. Launch the app with `streamlit run app.py`
2. Upload up to 10 PDFs
3. Click "Process Papers"
4. PDFs are parsed and text is extracted
5. Text is split into chunks (700 tokens, 80 overlap)
6. Embeddings are generated for each chunk
7. Vectorstore is created and saved to `vectorstore/` folder
8. Success message shows number of indexed chunks
9. Integrate LLM for answer generation (currently only retrieval)
10. Chat history added

**Option 2: Use Existing Vectorstore**
1. Click "Load Existing Database"
2. Previously processed vectorstore is loaded from `vectorstore/` folder

**Option 3: Ask Questions**
1. After processing or loading, enter a question in the text input
2. Click "Search"
3. The app retrieves top 3 most relevant chunks
4. Results are displayed with source attribution

## 📌 Upcoming Features


* Step 6: Add source highlighting and citation tracking
* Step 7: Deploy online
* Performance optimizations for large document collections

## 📄 Tech Stack

* **Python 3.x**
* **Streamlit** - Web UI framework
* **PyMuPDF (fitz)** - PDF text extraction
* **LangChain** - Text splitting, embeddings, vector store
* **HuggingFace Transformers** - Sentence embeddings (all-MiniLM-L6-v2)
* **FAISS** - Vector similarity search and storage

## 🔧 Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 👨‍💻 Author

Built as a hands-on AI/LLM project for learning Retrieval-Augmented Generation (RAG) systems.
