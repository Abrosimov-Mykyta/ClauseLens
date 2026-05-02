from pydantic import BaseModel


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
