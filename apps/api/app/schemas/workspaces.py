from pydantic import BaseModel


class WorkspaceSummary(BaseModel):
    id: str
    name: str
    status: str
    documents: int
    risks: int

