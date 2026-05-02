from fastapi import APIRouter

from app.schemas.audit import AuditEvent
from app.schemas.workspaces import WorkspaceDetail, WorkspaceSummary
from app.services.demo_store import get_workspace, list_audit_events, list_workspaces

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceSummary])
def get_workspaces() -> list[WorkspaceSummary]:
    return [WorkspaceSummary(**item) for item in list_workspaces()]


@router.get("/{workspace_id}", response_model=WorkspaceDetail)
def get_workspace_detail(workspace_id: str) -> WorkspaceDetail:
    workspace = get_workspace(workspace_id)
    if workspace is None:
        fallback = {
            "id": workspace_id,
            "name": "Unknown workspace",
            "status": "processing",
            "documents": 0,
            "risks": 0,
            "description": "Workspace not found in the demo store yet.",
            "members": 0,
            "recent_activity": [],
        }
        return WorkspaceDetail(**fallback)
    return WorkspaceDetail(**workspace)


@router.get("/{workspace_id}/audit", response_model=list[AuditEvent])
def get_workspace_audit(workspace_id: str) -> list[AuditEvent]:
    return [AuditEvent(**item) for item in list_audit_events(workspace_id)]
