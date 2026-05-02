import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.bootstrap import DEFAULT_USER_EMAIL
from app.models import (
    AnalysisRun,
    AuditLog,
    ChatMessage,
    ChatSession,
    Document,
    DocumentChunk,
    User,
    Workspace,
    WorkspaceMember,
)
from app.services.openai_chat import answer_with_openai


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


def serialize_analysis_snapshot(analysis: AnalysisRun | None) -> dict | None:
    if analysis is None:
        return None

    return {
        "id": analysis.id,
        "status": analysis.status,
        "summary": analysis.summary or "No summary generated yet.",
        "red_flags": analysis.red_flags or "No red flags captured yet.",
        "obligations": analysis.obligations or "No obligations captured yet.",
        "follow_up_questions": analysis.follow_up_questions
        or "No follow-up questions generated yet.",
        "created_at": analysis.created_at.isoformat(),
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
    documents = session.scalars(
        select(Document)
        .where(Document.workspace_id == workspace.id)
        .order_by(Document.created_at.desc())
        .limit(10)
    ).all()
    latest_analysis = session.scalar(
        select(AnalysisRun)
        .where(AnalysisRun.workspace_id == workspace.id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(1)
    )

    return {
        **summary,
        "description": workspace.description or "No description provided yet.",
        "members": member_count,
        "recent_activity": recent_activity_rows,
        "documents_list": [
            {
                "id": document.id,
                "filename": document.filename,
                "status": document.status,
                "stage": document.parser_stage,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            }
            for document in documents
        ],
        "latest_analysis": serialize_analysis_snapshot(latest_analysis),
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


def list_workspace_documents(session: Session, workspace_slug: str) -> list[dict]:
    workspace = get_workspace_by_slug(session, workspace_slug)
    if workspace is None:
        return []

    documents = session.scalars(
        select(Document)
        .where(Document.workspace_id == workspace.id)
        .order_by(Document.created_at.desc())
    ).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "status": document.status,
            "stage": document.parser_stage,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
        }
        for document in documents
    ]


def get_workspace_document_payload(
    session: Session,
    workspace_slug: str,
    document_id: str,
) -> dict | None:
    workspace = get_workspace_by_slug(session, workspace_slug)
    if workspace is None:
        return None

    document = session.scalar(
        select(Document)
        .where(Document.workspace_id == workspace.id, Document.id == document_id)
        .limit(1)
    )
    if document is None:
        return None

    latest_analysis = session.scalar(
        select(AnalysisRun)
        .where(AnalysisRun.document_id == document.id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(1)
    )
    chunks = session.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.chunk_index.asc())
    ).all()

    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status,
        "stage": document.parser_stage,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
        "mime_type": document.mime_type,
        "analysis_snapshot": serialize_analysis_snapshot(latest_analysis),
        "chunks": [
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "citation_label": chunk.citation_label
                or f"{document.filename}#chunk-{chunk.chunk_index + 1}",
                "content": chunk.content,
                "token_count": chunk.token_count,
            }
            for chunk in chunks
        ],
    }


def list_workspace_chat_history(session: Session, workspace_slug: str) -> list[dict]:
    workspace = get_workspace_by_slug(session, workspace_slug)
    if workspace is None:
        return []

    messages = session.scalars(
        select(ChatMessage)
        .join(ChatSession, ChatSession.id == ChatMessage.session_id)
        .where(ChatSession.workspace_id == workspace.id)
        .order_by(ChatMessage.created_at.asc())
    ).all()

    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "citations": message.citations.split("|") if message.citations else [],
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]


def _tokenize_query(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z]{3,}", text.lower())}


def _build_chat_context(session: Session, workspace: Workspace, question: str) -> list[dict[str, str]]:
    query_tokens = _tokenize_query(question)
    contexts: list[dict[str, str]] = []

    chunk_rows = session.execute(
        select(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.workspace_id == workspace.id)
        .order_by(Document.created_at.desc(), DocumentChunk.chunk_index.asc())
    ).all()

    for row in chunk_rows:
        chunk, document = row
        content_lower = chunk.content.lower()
        overlap_score = sum(1 for token in query_tokens if token in content_lower)
        contexts.append(
            {
                "type": "document_chunk",
                "label": document.filename,
                "citation": chunk.citation_label or f"{document.filename}#chunk-{chunk.chunk_index + 1}",
                "content": chunk.content,
                "score": overlap_score + 3,
            }
        )

    analysis_runs = session.scalars(
        select(AnalysisRun)
        .where(AnalysisRun.workspace_id == workspace.id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(3)
    ).all()

    for analysis in analysis_runs:
        if analysis.summary:
            analysis_sections = [
                ("summary", analysis.summary, 2),
                ("red_flags", analysis.red_flags or "", 3),
                ("obligations", analysis.obligations or "", 2),
                ("follow_up_questions", analysis.follow_up_questions or "", 1),
            ]
            for section_name, content, base_score in analysis_sections:
                overlap_score = sum(1 for token in query_tokens if token in content.lower())
                contexts.append(
                    {
                        "type": "analysis",
                        "label": f"analysis {section_name}",
                        "citation": f"analysis:{analysis.id}:{section_name}",
                        "content": content,
                        "score": overlap_score + base_score,
                    }
                )

    ranked_contexts = sorted(contexts, key=lambda item: item["score"], reverse=True)
    return ranked_contexts[:8]


def create_document_upload_record(
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
        parser_stage="queued",
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


def get_document_by_id(session: Session, document_id: str) -> Document | None:
    return session.scalar(select(Document).where(Document.id == document_id))


def claim_next_document_for_processing(session: Session) -> Document | None:
    document = session.scalar(
        select(Document)
        .where(Document.status == "uploaded", Document.parser_stage == "queued")
        .order_by(Document.created_at.asc())
        .limit(1)
    )
    if document is None:
        return None

    document.status = "processing"
    document.parser_stage = "parsing"
    session.add(document)
    session.add(
        AuditLog(
            workspace_id=document.workspace_id,
            actor_id=None,
            event_type="analysis.started",
            message=f"Started processing {document.filename}",
        )
    )
    session.commit()
    session.refresh(document)
    return document


def mark_document_stage(session: Session, document_id: str, *, status: str, parser_stage: str) -> Document:
    document = get_document_by_id(session, document_id)
    if document is None:
        raise ValueError("Document not found")

    document.status = status
    document.parser_stage = parser_stage
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def complete_document_processing(
    session: Session,
    document_id: str,
    *,
    chunks: list[str],
    analysis_payload: dict[str, str],
) -> Document:
    document = get_document_by_id(session, document_id)
    if document is None:
        raise ValueError("Document not found")

    workspace = session.scalar(select(Workspace).where(Workspace.id == document.workspace_id))
    if workspace is None:
        raise ValueError("Workspace not found")

    session.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()

    for index, chunk_text in enumerate(chunks):
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_text,
                token_count=len(chunk_text.split()),
                citation_label=f"{document.filename}#chunk-{index + 1}",
            )
        )

    analysis = AnalysisRun(
        workspace_id=workspace.id,
        document_id=document.id,
        status="completed",
        summary=analysis_payload["summary"],
        red_flags=analysis_payload["red_flags"],
        obligations=analysis_payload["obligations"],
        follow_up_questions=analysis_payload["follow_up_questions"],
    )
    session.add(analysis)

    actor = session.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    session.add(
        AuditLog(
            workspace_id=workspace.id,
            actor_id=actor.id if actor else None,
            event_type="analysis.completed",
            message=f"Generated initial analysis snapshot for {document.filename}",
        )
    )

    document.status = "ready"
    document.parser_stage = "analyzed"
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def fail_document_processing(session: Session, document_id: str, reason: str) -> Document:
    document = get_document_by_id(session, document_id)
    if document is None:
        raise ValueError("Document not found")

    document.status = "failed"
    document.parser_stage = "failed"
    session.add(document)

    actor = session.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    session.add(
        AuditLog(
            workspace_id=document.workspace_id,
            actor_id=actor.id if actor else None,
            event_type="analysis.failed",
            message=f"Document processing failed for {document.filename}: {reason}",
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

    chat_session = session.scalar(
        select(ChatSession)
        .where(ChatSession.workspace_id == workspace.id, ChatSession.user_id == actor.id)
        .order_by(ChatSession.created_at.desc())
        .limit(1)
    )
    if chat_session is None:
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

    contexts = _build_chat_context(session, workspace, question)
    response = answer_with_openai(question, workspace.name, contexts)
    citations = [str(citation) for citation in response.get("citations", [])]
    answer = str(response.get("answer", ""))
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
