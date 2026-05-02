from fastapi import APIRouter

from app.schemas.workspaces import WorkspaceSummary
from app.services.demo_store import list_workspaces

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceSummary])
def get_workspaces() -> list[WorkspaceSummary]:
    return [WorkspaceSummary(**item) for item in list_workspaces()]

