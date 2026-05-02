from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.schemas.documents import DocumentStatus
from app.services.chunker import chunk_document_text
from app.services.document_parser import extract_document_text
from app.services.openai_analysis import analyze_with_openai
from app.services.persistence import create_document_record

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentStatus)
async def upload_document(
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentStatus:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / file.filename
    contents = await file.read()
    target.write_bytes(contents)
    document_text = extract_document_text(str(target), file.content_type)
    chunks = chunk_document_text(document_text)
    analysis_payload = analyze_with_openai(file.filename, document_text)

    try:
        document = create_document_record(
            db,
            workspace_id,
            filename=file.filename,
            storage_path=str(target),
            mime_type=file.content_type,
            chunks=chunks,
            analysis_payload=analysis_payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return DocumentStatus(
        id=document.id,
        filename=document.filename,
        status=document.status,
        stage=document.parser_stage,
    )
