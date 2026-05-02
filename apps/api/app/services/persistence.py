from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.bootstrap import DEFAULT_USER_EMAIL
from app.models import AuditLog, ChatMessage, ChatSession, Document, User, Workspace, WorkspaceMember


def serialize_workspace_summary(session: Session, workspace: Workspace) -> dict:
    document_count = session.scalar(
        select(func.count(Document.id)).where(Document.workspace_id == workspace.id)
    ) or 0
    risk_count = max(1, document_count // 2) if document_count else 0

    return {
        "id": workspace.slug,
        "name": workspace.name,
        "status": workspace.status,
        "documents": document_count,
        "risks": risk_count,
    }


def list_workspace_summaries(session: Session) -> list[dict]:
    workspaces = session.scalars(select(Workspace).order_by(Workspace.created_at.asc())).all()
    return [serialize_workspace_summary(session, workspace) for workspace in workspaces]


def get_workspace_by_slug(session: Session, workspace_slug: str) -> Workspace | None:
    return session.scalar(select(Workspace).where(Workspace.slug == workspace_slug))


def get_workspace_detail_payload(session: Session, workspace_slug: str) -> dict | None:
    workspace = get_workspace_by_slug(session, workspace_slug)
    if workspace is None:
        return None

    summary = serialize_workspace_summary(session, workspace)
    member_count = session.scalar(
        select(func.count(WorkspaceMember.id)).where(WorkspaceMember.workspace_id == workspace.id)
    ) or 0
    recent_activity_rows = session.scalars(
        select(AuditLog.message)
        .where(AuditLog.workspace_id == workspace.id)
        .order_by(AuditLog.created_at.desc())
        .limit(4)
    ).all()

    return {
        **summary,
        "description": workspace.description or "No description provided yet.",
        "members": member_count,
        "recent_activity": recent_activity_rows,
    }


def list_workspace_audit_events(session: Session, workspace_slug: str) -> list[dict]:
    workspace = get_workspace_by_slug(session, workspace_slug)
    if workspace is None:
        return []

    events = session.scalars(
        select(AuditLog)
        .where(AuditLog.workspace_id == workspace.id)
        .order_by(AuditLog.created_at.desc())
        .limit(20)
    ).all()

    return [
        {
            "id": event.id,
            "event_type": event.event_type,
            "message": event.message,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]


def create_document_record(
    session: Session,
    workspace_slug: str,
    *,
    filename: str,
    storage_path: str,
    mime_type: str | None,
) -> Document:
    workspace = get_workspace_by_slug(session, workspace_slug)
    if workspace is None:
        raise ValueError("Workspace not found")

    document = Document(
        workspace_id=workspace.id,
        filename=filename,
        storage_path=storage_path,
        mime_type=mime_type,
        status="uploaded",
        parser_stage="queued-for-processing",
    )
    session.add(document)
    session.flush()

    actor = session.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    session.add(
        AuditLog(
            workspace_id=workspace.id,
            actor_id=actor.id if actor else None,
            event_type="document.uploaded",
            message=f"Uploaded {filename}",
        )
    )
    session.commit()
    session.refresh(document)
    return document


def create_chat_exchange(session: Session, workspace_slug: str, question: str) -> dict:
    workspace = get_workspace_by_slug(session, workspace_slug)
    if workspace is None:
        raise ValueError("Workspace not found")

    actor = session.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    if actor is None:
        raise ValueError("Demo reviewer not found")

    chat_session = ChatSession(
        workspace_id=workspace.id,
        user_id=actor.id,
        title="Due diligence review",
    )
    session.add(chat_session)
    session.flush()

    user_message = ChatMessage(
        session_id=chat_session.id,
        role="user",
        content=question,
    )

    citations = [
        f"{workspace.slug}-document-summary#overview",
        f"{workspace.slug}-risk-register#top-items",
    ]
    answer = (
        f"ClauseLens reviewed the indexed material for {workspace.name} and would start with "
        f"change-of-control language, indemnity exposure, and termination mechanics before "
        f"answering the question: '{question}'."
    )
    assistant_message = ChatMessage(
        session_id=chat_session.id,
        role="assistant",
        content=answer,
        citations="|".join(citations),
    )

    session.add_all([user_message, assistant_message])
    session.add(
        AuditLog(
            workspace_id=workspace.id,
            actor_id=actor.id,
            event_type="chat.question_asked",
            message=f"Reviewer asked: {question}",
        )
    )
    session.commit()

    return {
        "answer": answer,
        "citations": citations,
    }
