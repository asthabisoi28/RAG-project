from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import LLMQuotaError, NotFoundError
from app.models.schemas import ChatMessage, ChatResponse, DocumentInfo, Source
from app.services.chunker import TextChunker
from app.services.document_loader import DocumentLoader
from app.services.embeddings import EmbeddingService
from app.services.llm import get_llm_client
from app.services.vector_store import VectorStore


class RAGService:
    def __init__(self):
        storage_root = Path(settings.storage_dir)
        self.loader = DocumentLoader(storage_root / "uploads")
        self.chunker = TextChunker(settings.chunk_size, settings.chunk_overlap)
        self.embeddings = EmbeddingService(settings.embedding_model)
        self.store = VectorStore(storage_root / "index", self.embeddings.dimension)

    async def ingest(self, files: list[UploadFile]) -> list[DocumentInfo]:
        documents: list[DocumentInfo] = []
        for file in files:
            document_id, filename, _, pages = await self.loader.save_and_extract(file)
            chunks = self.chunker.split_pages(document_id, filename, pages)
            vectors = self.embeddings.embed([chunk.text for chunk in chunks])
            info = DocumentInfo(id=document_id, filename=filename, pages=len(pages), chunks=len(chunks))
            self.store.add_document(info, chunks, vectors)
            documents.append(info)
        return documents

    async def chat(self, message: str, top_k: int, history: list[ChatMessage]) -> ChatResponse:
        if not self.store.chunks:
            raise NotFoundError("Upload at least one PDF before asking questions")
        query_vector = self.embeddings.embed([message])
        sources = self.store.search(query_vector, top_k)
        try:
            answer = await get_llm_client(settings).answer(message, sources, history)
        except LLMQuotaError:
            answer = build_retrieval_fallback_answer(sources)
        return ChatResponse(answer=answer, sources=sources)

    def list_documents(self) -> list[DocumentInfo]:
        return self.store.list_documents()

    def delete_document(self, document_id: str) -> tuple[int, int]:
        if not self.store.document_exists(document_id):
            raise NotFoundError("Document not found")

        documents = {key: value for key, value in self.store.documents.items() if key != document_id}
        chunks = self.store.chunks_excluding_document(document_id)
        embeddings = self.embeddings.embed([chunk["text"] for chunk in chunks])
        self.store.rebuild(documents, chunks, embeddings)
        self._delete_uploaded_files(document_id)
        return self.store.stats()

    def stats(self) -> tuple[int, int]:
        return self.store.stats()

    def _delete_uploaded_files(self, document_id: str) -> None:
        for path in self.loader.upload_dir.glob(f"{document_id}_*"):
            if path.is_file():
                path.unlink(missing_ok=True)


rag_service = RAGService()


def build_retrieval_fallback_answer(sources: list[Source]) -> str:
    if not sources:
        return (
            "I found no relevant document chunks for that question. "
            "The LLM provider is also unavailable because its quota is exhausted."
        )

    excerpts = []
    for index, source in enumerate(sources[:3], start=1):
        text = source.text.strip()
        if len(text) > 700:
            text = f"{text[:700].rsplit(' ', 1)[0]}..."
        excerpts.append(f"[{index}] {source.filename}, page {source.page}: {text}")

    return (
        "The LLM provider quota is exhausted, so I cannot generate a full natural-language answer right now. "
        "Here are the most relevant retrieved passages from your documents:\n\n"
        + "\n\n".join(excerpts)
    )
