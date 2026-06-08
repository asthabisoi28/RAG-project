from pydantic import BaseModel, Field


class DocumentInfo(BaseModel):
    id: str
    filename: str
    pages: int
    chunks: int


class UploadResponse(BaseModel):
    documents: list[DocumentInfo]


class DeleteDocumentResponse(BaseModel):
    deleted_document_id: str
    documents: int
    chunks: int


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=12)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class Source(BaseModel):
    document_id: str
    filename: str
    page: int
    chunk_id: str
    score: float
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class HealthResponse(BaseModel):
    status: str
    documents: int
    chunks: int
