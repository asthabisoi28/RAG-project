from pathlib import Path
from uuid import uuid4

import fitz
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import InvalidFileError


class DocumentLoader:
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_and_extract(self, file: UploadFile) -> tuple[str, str, Path, list[tuple[int, str]]]:
        self._validate_pdf(file)
        content = await file.read()
        if len(content) > settings.max_upload_bytes:
            raise InvalidFileError(f"{file.filename} exceeds {settings.max_upload_size_mb} MB")

        document_id = str(uuid4())
        safe_name = Path(file.filename or "document.pdf").name
        destination = self.upload_dir / f"{document_id}_{safe_name}"
        destination.write_bytes(content)

        try:
            pages = self._extract_pages(destination)
        except Exception as exc:
            destination.unlink(missing_ok=True)
            raise InvalidFileError(f"{safe_name} could not be parsed as a valid PDF") from exc

        if not any(text.strip() for _, text in pages):
            destination.unlink(missing_ok=True)
            raise InvalidFileError(f"{safe_name} does not contain extractable text")

        return document_id, safe_name, destination, pages

    def _validate_pdf(self, file: UploadFile) -> None:
        filename = file.filename or ""
        if not filename.lower().endswith(".pdf"):
            raise InvalidFileError(f"{filename or 'Uploaded file'} is not a PDF")
        if file.content_type not in {"application/pdf", "application/octet-stream"}:
            raise InvalidFileError(f"{filename} has invalid content type: {file.content_type}")

    def _extract_pages(self, path: Path) -> list[tuple[int, str]]:
        pages: list[tuple[int, str]] = []
        with fitz.open(path) as pdf:
            if pdf.page_count == 0:
                raise InvalidFileError("PDF has no pages")
            for index, page in enumerate(pdf, start=1):
                pages.append((index, page.get_text("text")))
        return pages

