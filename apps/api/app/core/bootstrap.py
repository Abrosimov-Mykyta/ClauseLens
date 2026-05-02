from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog, User, Workspace, WorkspaceMember

DEFAULT_USER_EMAIL = "reviewer@clauselens.local"

DEFAULT_WORKSPACES = [
    {
        "name": "Acme Acquisition Review",
        "slug": "ws-acme",
        "description": "Cross-document review for a mid-market acquisition data room.",
        "status": "ready",
        "audit": [
            ("document.uploaded", "Uploaded supplier-agreement.pdf"),
            ("analysis.completed", "Generated red flag summary for the latest review batch"),
            ("chat.question_asked", "Reviewer asked about indemnity exposure"),
        ],
    },
    {
        "name": "Northstar Vendor Audit",
        "slug": "ws-northstar",
        "description": "Ongoing procurement review with fresh uploads still parsing.",
        "status": "processing",
        "audit": [
            ("document.uploaded", "Uploaded nda-draft.pdf"),
            ("document.processing", "Employment agreement queued for chunking"),
            ("audit.stream_active", "Audit timeline available for reviewer follow-up"),
        ],
    },
]


def seed_database(session: Session) -> None:
    user = session.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    if user is None:
        user = User(email=DEFAULT_USER_EMAIL, full_name="Demo Reviewer")
        session.add(user)
        session.flush()

    for workspace_data in DEFAULT_WORKSPACES:
        workspace = session.scalar(select(Workspace).where(Workspace.slug == workspace_data["slug"]))
        if workspace is None:
            workspace = Workspace(
                name=workspace_data["name"],
                slug=workspace_data["slug"],
                description=workspace_data["description"],
                status=workspace_data["status"],
            )
            session.add(workspace)
            session.flush()

            session.add(
                WorkspaceMember(
                    workspace_id=workspace.id,
                    user_id=user.id,
                    role="owner",
                )
            )

            for event_type, message in workspace_data["audit"]:
                session.add(
                    AuditLog(
                        workspace_id=workspace.id,
                        actor_id=user.id,
                        event_type=event_type,
                        message=message,
                    )
                )

    session.commit()
