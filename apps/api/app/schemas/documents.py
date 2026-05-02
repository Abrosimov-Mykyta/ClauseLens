from pydantic import BaseModel


class DocumentStatus(BaseModel):
    id: str
    filename: str
    status: str
    stage: str


class DocumentSummary(DocumentStatus):
    created_at: str
