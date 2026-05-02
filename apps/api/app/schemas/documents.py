from pydantic import BaseModel

from app.schemas.analysis import AnalysisSnapshot


class DocumentStatus(BaseModel):
    id: str
    filename: str
    status: str
    stage: str


class DocumentSummary(DocumentStatus):
    created_at: str
    updated_at: str


class DocumentChunkExcerpt(BaseModel):
    id: str
    chunk_index: int
    citation_label: str
    content: str
    token_count: int | None


class DocumentDetail(DocumentSummary):
    mime_type: str | None
    analysis_snapshot: AnalysisSnapshot | None
    chunks: list[DocumentChunkExcerpt]
