from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from app.core.config import settings
from app.schemas.documents import DocumentStatus

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentStatus)
async def upload_document(file: UploadFile = File(...)) -> DocumentStatus:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / file.filename
    contents = await file.read()
    target.write_bytes(contents)

    return DocumentStatus(
        id=f"doc-{file.filename}",
        filename=file.filename,
        status="uploaded",
        stage="queued-for-processing",
    )

