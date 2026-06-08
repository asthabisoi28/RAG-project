# AI Chat with Document Search (RAG)

A full-stack Retrieval Augmented Generation application built with **FastAPI**, **FAISS**, **Sentence Transformers**, **PyMuPDF**, **Gemini/OpenAI**, and **React + Tailwind CSS**.

The app allows users to upload PDF documents, search them semantically, ask questions in a chat interface, and receive answers with source citations from the uploaded documents.

## Features

- Upload one or more PDF documents
- Extract text from PDFs using PyMuPDF
- Split extracted text into meaningful chunks
- Generate embeddings with Sentence Transformers
- Store and search embeddings using FAISS
- Ask questions about uploaded PDFs
- Generate answers using Gemini or OpenAI
- Show source citations with filename, page number, score, and retrieved text
- Delete uploaded documents from the index
- Persist document metadata and vector index locally
- Responsive React + Tailwind UI
- Chat history, loading states, and error handling

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- PyMuPDF
- Sentence Transformers
- FAISS
- NumPy
- OpenAI API
- Google Gemini API

### Frontend

- React
- Vite
- Tailwind CSS
- Lucide React icons
- Fetch API

### Storage

- Local PDF storage
- Local FAISS index
- JSON metadata for documents and chunks

## Project Structure

```text
.
|-- backend
|   |-- app
|   |   |-- api
|   |   |   `-- routes.py
|   |   |-- core
|   |   |   |-- config.py
|   |   |   `-- exceptions.py
|   |   |-- models
|   |   |   `-- schemas.py
|   |   |-- services
|   |   |   |-- chunker.py
|   |   |   |-- document_loader.py
|   |   |   |-- embeddings.py
|   |   |   |-- llm.py
|   |   |   |-- rag.py
|   |   |   `-- vector_store.py
|   |   `-- main.py
|   |-- requirements.txt
|   `-- .env.example
|-- frontend
|   |-- src
|   |   |-- api
|   |   |   `-- client.js
|   |   |-- components
|   |   |   |-- ChatPanel.jsx
|   |   |   |-- DocumentPanel.jsx
|   |   |   `-- SourceList.jsx
|   |   |-- App.jsx
|   |   |-- main.jsx
|   |   `-- styles.css
|   |-- package.json
|   |-- tailwind.config.js
|   `-- vite.config.js
|-- README.md
`-- .gitignore
```

## How It Works

1. User uploads PDF files from the frontend.
2. FastAPI validates the files and saves them locally.
3. PyMuPDF extracts text page by page.
4. The text is split into overlapping chunks.
5. Sentence Transformers generate embeddings for each chunk.
6. FAISS stores normalized embeddings for semantic search.
7. When the user asks a question, the question is embedded and searched against FAISS.
8. The most relevant chunks are sent to Gemini or OpenAI as context.
9. The LLM generates an answer with citations.
10. The frontend displays the answer and expandable source references.

## Backend Setup

Open a terminal:

```powershell
cd "C:\Users\asbi1\Documents\RAG project\backend"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend\.env`.

For Gemini:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

### Important Technical Decisions

- **FAISS IndexFlatIP + normalized embeddings**: cosine similarity without a training step, simple and reliable for an internship-scale project.
- **Local persistence**: uploaded files, document metadata, chunks, and FAISS indexes survive restarts without adding database infrastructure.
- **Provider abstraction for LLMs**: OpenAI and Gemini are isolated behind one interface, so the API layer does not know vendor details.
- **Structured citations**: every answer returns source filename, page number, chunk id, and score for transparent grounding.
- **Modular services**: parsing, chunking, embeddings, vector storage, generation, and orchestration are separate modules for maintainability.
- **Defensive validation**: file type, file size, empty PDFs, missing indexes, and LLM configuration errors are handled explicitly.


## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash
```

## Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

In local development, the frontend calls `/api/*` and Vite proxies those requests to `http://localhost:8000`. For deployment, set `VITE_API_BASE_URL` to the backend URL.

## REST API

### Health

`GET /api/health`

Returns service status and current index statistics.

### Upload PDFs

`POST /api/documents/upload`

Multipart field: `files`

Accepts one or more PDF files and returns indexed document metadata.

### List Documents

`GET /api/documents`

Returns documents currently known to the local store.

### Chat

`POST /api/chat`

```json
{
  "message": "What are the key findings?",
  "top_k": 5,
  "history": [
    { "role": "user", "content": "Summarize the document" },
    { "role": "assistant", "content": "..." }
  ]
}
```

Returns:

```json
{
  "answer": "...",
  "sources": [
    {
      "document_id": "...",
      "filename": "paper.pdf",
      "page": 3,
      "chunk_id": "...",
      "score": 0.81,
      "text": "..."
    }
  ]
}
```

## Deployment

### Backend

1. Create a production `.env`.
2. Install dependencies in a virtual environment.
3. Run with Gunicorn/Uvicorn workers:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000
```

4. Mount `backend/storage` as persistent disk storage.
5. Put Nginx or a cloud load balancer in front for TLS and upload limits.

### Frontend

```bash
cd frontend
npm run build
```

Serve `frontend/dist` from Vercel, Netlify, Nginx, or any static host. Set `VITE_API_BASE_URL` to the deployed backend URL.

## Production Notes

- Replace local JSON metadata with Postgres for multi-user production.
- Replace local file storage with S3/GCS/Azure Blob for horizontal scaling.
- Use background workers for large PDF ingestion.
- Add authentication and per-user/tenant indexes before exposing publicly.
- Add observability for upload latency, retrieval score distributions, and LLM failures.
