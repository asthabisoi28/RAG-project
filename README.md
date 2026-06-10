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

```

## Backend Setup

Open a terminal:

```powershell
cd "C:\Users\asbi1\Documents\RAG project\backend"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```


Start the backend:

```powershell
uvicorn app.main:app --reload --port 8000
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open a second terminal:

```powershell
cd "C:\Users\asbi1\Documents\RAG project\frontend"
npm install
npm run dev


Frontend app:

```text
http://127.0.0.1:5173
```

In local development, Vite proxies `/api/*` requests to `http://127.0.0.1:8000`.

## API Endpoints

### Health Check

```http
GET /api/health
```

Returns backend status and index statistics.

### Upload Documents

```http
POST /api/documents/upload
```

Form field:

```text
files
```

Supports multiple PDF uploads.

### List Documents

```http
GET /api/documents
```

Returns all indexed documents.

### Delete Document

```http
DELETE /api/documents/{document_id}
```

Deletes the document metadata, chunks, uploaded PDF file, and rebuilds the FAISS index.

### Chat

```http
POST /api/chat
```

Request:

```json
{
  "message": "Summarize the uploaded PDFs",
  "top_k": 5,
  "history": []
}
```

Response:

```json
{
  "answer": "The documents describe...",
  "sources": [
    {
      "document_id": "document-id",
      "filename": "example.pdf",
      "page": 1,
      "chunk_id": "chunk-id",
      "score": 0.82,
      "text": "Retrieved source text..."
    }
  ]
}
```

## Environment Variables

Backend variables are stored in:

```text
backend/.env
```

Important variables:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=900
CHUNK_OVERLAP=180
TOP_K=5
MAX_UPLOAD_SIZE_MB=25
```

## Common Issues

### Connection refused on port 8000

The backend is not running. Start it with:

```powershell
cd "C:\Users\asbi1\Documents\RAG project\backend"
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### OpenAI or Gemini quota error

The API key is valid, but the provider account/project has no available quota. Add billing/quota, use another key, or switch providers in `backend/.env`.

### Old files appear in citations

The app persists uploaded documents in `backend/storage`. Delete unwanted files from the UI using the trash button, or clear the storage folder during development.

## Deployment Notes

### Docker Compose

Create `backend/.env` first, then run both services:

```bash
docker compose up --build
```

Frontend:

```text
http://localhost:3000
```

Backend:

```text
http://localhost:8000
```

The backend stores uploaded PDFs, metadata, and FAISS files in the `backend_storage` Docker volume.

### Backend

- Use a production `.env`.
- Run with Uvicorn/Gunicorn.
- Persist `backend/storage`.
- Put Nginx or a cloud load balancer in front.
- Configure upload size limits.

Example:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000
```

### Frontend

Build the frontend:

```bash
cd frontend
npm run build
```

Deploy `frontend/dist` to Vercel, Netlify, Nginx, or any static hosting provider.

For deployment, set:

```env
VITE_API_BASE_URL=https://your-backend-domain.com
```
