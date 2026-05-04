from pydantic import BaseModel

from app.schemas.analysis import AnalysisSnapshot
from app.schemas.documents import DocumentSummary


class RetrievalMetrics(BaseModel):
    indexed_documents: int
    indexed_chunks: int
    embedded_chunks: int
    analysis_runs: int


class WorkspaceSummary(BaseModel):
    id: str
    name: str
    status: str
    documents: int
    risks: int


class WorkspaceDetail(WorkspaceSummary):
    description: str
    members: int
    recent_activity: list[str]
    documents_list: list[DocumentSummary]
    latest_analysis: AnalysisSnapshot | None
    retrieval_metrics: RetrievalMetrics
