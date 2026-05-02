from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    PdfReader = None


TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".html",
    ".htm",
    ".rtf",
}


def extract_document_text(file_path: str, mime_type: str | None = None) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf" and PdfReader is not None:
        try:
            reader = PdfReader(file_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            pdf_text = "\n\n".join(page.strip() for page in pages if page.strip())
            if pdf_text:
                return pdf_text
        except Exception:
            pass

    raw_bytes = path.read_bytes()

    if mime_type and mime_type.startswith("text/"):
        return raw_bytes.decode("utf-8", errors="replace")

    if suffix in TEXT_EXTENSIONS:
        return raw_bytes.decode("utf-8", errors="replace")

    decoded_preview = raw_bytes.decode("utf-8", errors="replace").strip()
    if decoded_preview:
        return decoded_preview

    return (
        f"Binary document uploaded: {path.name}. No text extraction is currently available for "
        f"this file type in the local MVP parser."
    )
