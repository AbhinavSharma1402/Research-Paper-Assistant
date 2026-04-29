# Research Paper Assistant

A Streamlit-based application that allows users to upload multiple research papers (PDFs), extract text, and prepare the content for semantic search and question answering.

## 🚀 Current Progress (Up to Step 2)

### ✅ Step 1: Multi-PDF Upload Interface

Users can upload up to 10 PDF research papers through a clean Streamlit UI.

**Features:**

* Multiple file upload support
* PDF-only validation
* Maximum 10 files allowed
* Uploaded files saved locally in the `uploads/` folder
* Success/error messages in the UI

### ✅ Step 2: PDF Text Extraction + Chunking

Uploaded PDFs are processed and converted into text using PyMuPDF.
The extracted text is then split into smaller chunks for later retrieval and embeddings.

**Libraries Used:**

* `PyMuPDF (fitz)` for PDF parsing
* `RecursiveCharacterTextSplitter` from LangChain for chunking

**Chunk Settings:**

* `chunk_size = 1000`
* `chunk_overlap = 200`

**Stored Output Format:**
Each chunk is stored with source metadata:

```python
{
  "text": "chunk content...",
  "source": "paper_name.pdf"
}
```

## 📁 Project Structure

```text
Research-Paper-Assistant/
├── app.py
├── uploads/
├── README.md
└── requirements.txt
```

## 🛠️ Installation

```bash
pip install streamlit pymupdf langchain-text-splitters
```

## ▶️ Run the App

```bash
streamlit run app.py
```

## 🧪 Current Workflow

1. Launch the app
2. Upload up to 10 PDFs
3. Files are saved locally
4. Text is extracted from each PDF
5. Text is split into chunks
6. Preview of processed chunks shown in the UI
7. Vhinks converted into  embeddings
8. Store vectors in FAISS

## 📌 Upcoming Steps

* Step 5: Ask questions across papers (RAG)
* Step 6: Deploy online

## 📄 Tech Stack

* Python
* Streamlit
* PyMuPDF
* LangChain

## 👨‍💻 Author

Built as a hands-on AI/LLM project for learning Retrieval-Augmented Generation (RAG) systems.
