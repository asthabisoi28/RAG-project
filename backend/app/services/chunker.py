from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class TextChunk:
    id: str
    document_id: str
    filename: str
    page: int
    text: str


class TextChunker:
    def __init__(self, chunk_size: int, overlap: int):
        if overlap >= chunk_size:
            raise ValueError("chunk overlap must be smaller than chunk size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_pages(self, document_id: str, filename: str, pages: list[tuple[int, str]]) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        for page_number, text in pages:
            for part in self._split_text(text):
                clean = " ".join(part.split())
                if clean:
                    chunks.append(
                        TextChunk(
                            id=str(uuid4()),
                            document_id=document_id,
                            filename=filename,
                            page=page_number,
                            text=clean,
                        )
                    )
        return chunks

    def _split_text(self, text: str) -> list[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            if len(paragraph) > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(self._split_long_text(paragraph))
                continue

            candidate = f"{current}\n\n{paragraph}".strip()
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = paragraph

        if current:
            chunks.append(current)
        return self._apply_overlap(chunks)

    def _split_long_text(self, text: str) -> list[str]:
        words = text.split()
        chunks: list[str] = []
        current: list[str] = []
        length = 0

        for word in words:
            if length + len(word) + 1 > self.chunk_size and current:
                chunks.append(" ".join(current))
                current = []
                length = 0
            current.append(word)
            length += len(word) + 1

        if current:
            chunks.append(" ".join(current))
        return chunks

    def _apply_overlap(self, chunks: list[str]) -> list[str]:
        if not chunks or self.overlap <= 0:
            return chunks

        overlapped = [chunks[0]]
        for chunk in chunks[1:]:
            tail = self._last_words(overlapped[-1])
            overlapped.append(f"{tail} {chunk}")
        return overlapped

    def _last_words(self, text: str) -> str:
        words = text.split()
        selected: list[str] = []
        length = 0
        for word in reversed(words):
            if length + len(word) + 1 > self.overlap and selected:
                break
            selected.append(word)
            length += len(word) + 1
        return " ".join(reversed(selected))
