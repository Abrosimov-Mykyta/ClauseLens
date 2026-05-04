from sqlalchemy.orm import Session

from app.services.chunker import chunk_document_text
from app.services.document_parser import extract_document_text
from app.services.openai_analysis import analyze_with_openai
from app.services.openai_embeddings import embed_texts
from app.services.persistence import (
    complete_document_processing,
    fail_document_processing,
    get_document_by_id,
    mark_document_stage,
)


def process_document(session: Session, document_id: str) -> dict[str, str]:
    document = get_document_by_id(session, document_id)
    if document is None:
        raise ValueError("Document not found")

    try:
        mark_document_stage(session, document_id, status="processing", parser_stage="parsing")
        document = get_document_by_id(session, document_id)
        if document is None:
            raise ValueError("Document not found after parsing transition")

        document_text = extract_document_text(document.storage_path, document.mime_type)

        mark_document_stage(session, document_id, status="processing", parser_stage="chunking")
        chunks = chunk_document_text(document_text)
        if not chunks and document_text.strip():
            chunks = [document_text.strip()]
        chunk_embeddings = embed_texts(chunks)

        mark_document_stage(session, document_id, status="processing", parser_stage="analyzing")
        analysis_payload = analyze_with_openai(document.filename, document_text)

        complete_document_processing(
            session,
            document_id,
            chunks=chunks,
            chunk_embeddings=chunk_embeddings,
            analysis_payload=analysis_payload,
        )

        return {
            "document_id": document_id,
            "status": "ready",
            "stage": "analyzed",
        }
    except Exception as exc:
        fail_document_processing(session, document_id, str(exc))
        return {
            "document_id": document_id,
            "status": "failed",
            "stage": "failed",
        }
