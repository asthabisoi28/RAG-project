from fastapi import APIRouter, File, UploadFile

from app.core.config import settings
from app.core.exceptions import InvalidFileError
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    DeleteDocumentResponse,
    DocumentInfo,
    HealthResponse,
    UploadResponse,
)
from app.services.rag import rag_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    documents, chunks = rag_service.stats()
    return HealthResponse(status="ok", documents=documents, chunks=chunks)


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)) -> UploadResponse:
    if not files:
        raise InvalidFileError("At least one PDF file is required")
    if len(files) > 10:
        raise InvalidFileError("Upload at most 10 PDFs at a time")
    documents = await rag_service.ingest(files)
    return UploadResponse(documents=documents)


@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents() -> list[DocumentInfo]:
    return rag_service.list_documents()


@router.delete("/documents/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(document_id: str) -> DeleteDocumentResponse:
    documents, chunks = rag_service.delete_document(document_id)
    return DeleteDocumentResponse(deleted_document_id=document_id, documents=documents, chunks=chunks)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    top_k = request.top_k or settings.top_k
    return await rag_service.chat(request.message, top_k, request.history)
