from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.audit import AuditEvent
from app.schemas.chat import ChatHistoryMessage
from app.schemas.documents import DocumentDetail, DocumentSummary
from app.schemas.workspaces import WorkspaceDetail, WorkspaceSummary
from app.services.persistence import (
    get_workspace_detail_payload,
    get_workspace_document_payload,
    list_workspace_chat_history,
    list_workspace_documents,
    list_workspace_audit_events,
    list_workspace_summaries,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceSummary])
def get_workspaces(db: Session = Depends(get_db)) -> list[WorkspaceSummary]:
    return [WorkspaceSummary(**item) for item in list_workspace_summaries(db)]


@router.get("/{workspace_id}", response_model=WorkspaceDetail)
def get_workspace_detail(workspace_id: str, db: Session = Depends(get_db)) -> WorkspaceDetail:
    workspace = get_workspace_detail_payload(db, workspace_id)
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
            "documents_list": [],
            "latest_analysis": None,
        }
        return WorkspaceDetail(**fallback)
    return WorkspaceDetail(**workspace)


@router.get("/{workspace_id}/audit", response_model=list[AuditEvent])
def get_workspace_audit(
    workspace_id: str,
    db: Session = Depends(get_db),
) -> list[AuditEvent]:
    return [AuditEvent(**item) for item in list_workspace_audit_events(db, workspace_id)]


@router.get("/{workspace_id}/documents", response_model=list[DocumentSummary])
def get_workspace_documents(
    workspace_id: str,
    db: Session = Depends(get_db),
) -> list[DocumentSummary]:
    return [DocumentSummary(**item) for item in list_workspace_documents(db, workspace_id)]


@router.get("/{workspace_id}/documents/{document_id}", response_model=DocumentDetail)
def get_workspace_document(
    workspace_id: str,
    document_id: str,
    db: Session = Depends(get_db),
) -> DocumentDetail:
    payload = get_workspace_document_payload(db, workspace_id, document_id)
    if payload is None:
        fallback = {
            "id": document_id,
            "filename": "Unknown document",
            "status": "missing",
            "stage": "unavailable",
            "created_at": "",
            "updated_at": "",
            "mime_type": None,
            "analysis_snapshot": None,
            "chunks": [],
        }
        return DocumentDetail(**fallback)
    return DocumentDetail(**payload)


@router.get("/{workspace_id}/chat/history", response_model=list[ChatHistoryMessage])
def get_workspace_chat_history(
    workspace_id: str,
    db: Session = Depends(get_db),
) -> list[ChatHistoryMessage]:
    return [ChatHistoryMessage(**item) for item in list_workspace_chat_history(db, workspace_id)]
