import re


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_document_text(
    document_text: str,
    *,
    target_size: int = 700,
    overlap: int = 120,
) -> list[str]:
    normalized = _normalize_whitespace(document_text)
    if not normalized:
        return []

    if len(normalized) <= target_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    text_length = len(normalized)

    while start < text_length:
        end = min(start + target_size, text_length)
        if end < text_length:
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + 120:
                end = boundary

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(end - overlap, 0)

    return chunks

