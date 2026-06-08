import json
from pathlib import Path

import faiss
import numpy as np

from app.models.schemas import DocumentInfo, Source
from app.services.chunker import TextChunk


class VectorStore:
    def __init__(self, storage_dir: Path, dimension: int):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.storage_dir / "faiss.index"
        self.chunks_path = self.storage_dir / "chunks.json"
        self.documents_path = self.storage_dir / "documents.json"
        self.dimension = dimension
        self.index = self._load_index()
        self.chunks = self._load_json(self.chunks_path, [])
        self.documents = self._load_json(self.documents_path, {})

    def add_document(self, info: DocumentInfo, chunks: list[TextChunk], embeddings: np.ndarray) -> None:
        if embeddings.shape[0] != len(chunks):
            raise ValueError("embedding count must match chunk count")
        self.index.add(embeddings)
        self.chunks.extend([chunk.__dict__ for chunk in chunks])
        self.documents[info.id] = info.model_dump()
        self.persist()

    def document_exists(self, document_id: str) -> bool:
        return document_id in self.documents

    def chunks_excluding_document(self, document_id: str) -> list[dict]:
        return [chunk for chunk in self.chunks if chunk["document_id"] != document_id]

    def rebuild(self, documents: dict, chunks: list[dict], embeddings: np.ndarray) -> None:
        if embeddings.shape[0] != len(chunks):
            raise ValueError("embedding count must match chunk count")
        self.index = faiss.IndexFlatIP(self.dimension)
        if len(chunks) > 0:
            self.index.add(embeddings)
        self.documents = documents
        self.chunks = chunks
        self.persist()

    def search(self, query_embedding: np.ndarray, top_k: int) -> list[Source]:
        if self.index.ntotal == 0:
            return []
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        results: list[Source] = []
        for score, index in zip(scores[0], indices[0], strict=False):
            if index < 0:
                continue
            chunk = self.chunks[int(index)]
            if chunk["document_id"] not in self.documents:
                continue
            results.append(
                Source(
                    document_id=chunk["document_id"],
                    filename=chunk["filename"],
                    page=chunk["page"],
                    chunk_id=chunk["id"],
                    score=float(score),
                    text=chunk["text"],
                )
            )
        return results

    def list_documents(self) -> list[DocumentInfo]:
        return [DocumentInfo(**doc) for doc in self.documents.values()]

    def stats(self) -> tuple[int, int]:
        return len(self.documents), len(self.chunks)

    def persist(self) -> None:
        faiss.write_index(self.index, str(self.index_path))
        self.chunks_path.write_text(json.dumps(self.chunks, indent=2), encoding="utf-8")
        self.documents_path.write_text(json.dumps(self.documents, indent=2), encoding="utf-8")

    def _load_index(self):
        if self.index_path.exists():
            index = faiss.read_index(str(self.index_path))
            if index.d != self.dimension:
                raise ValueError(
                    f"FAISS index dimension {index.d} does not match embedding model dimension {self.dimension}. "
                    "Clear storage/index or use the original embedding model."
                )
            return index
        return faiss.IndexFlatIP(self.dimension)

    def _load_json(self, path: Path, default):
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
