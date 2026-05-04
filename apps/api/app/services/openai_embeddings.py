import hashlib
import json
import math
from typing import Any
from urllib import error, request

from app.core.config import settings

FALLBACK_EMBEDDING_DIMENSIONS = 64


def _normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(component * component for component in vector))
    if magnitude == 0:
        return vector

    return [component / magnitude for component in vector]


def build_fallback_embedding(text: str, *, dimensions: int = FALLBACK_EMBEDDING_DIMENSIONS) -> list[float]:
    vector = [0.0] * dimensions
    normalized_text = " ".join(text.lower().split())
    if not normalized_text:
        return vector

    for token in normalized_text.split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:2], "big") % dimensions
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        weight = 1.0 + (digest[3] / 255.0)
        vector[bucket] += sign * weight

    return _normalize(vector)


def _extract_embeddings(payload: dict[str, Any]) -> list[list[float]]:
    data = payload.get("data", [])
    embeddings: list[list[float]] = []
    for item in data:
        embedding = item.get("embedding")
        if isinstance(embedding, list):
            embeddings.append([float(component) for component in embedding])

    if not embeddings:
        raise ValueError("No embeddings returned from OpenAI response")

    return embeddings


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    if not settings.openai_api_key:
        return [build_fallback_embedding(text) for text in texts]

    body = {
        "model": settings.openai_embedding_model,
        "input": texts,
    }

    http_request = request.Request(
        settings.openai_embeddings_url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=60) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
        embeddings = _extract_embeddings(response_payload)
    except (error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError, ValueError, TypeError):
        return [build_fallback_embedding(text) for text in texts]

    return [_normalize(embedding) for embedding in embeddings]


def embed_text(text: str) -> list[float]:
    embeddings = embed_texts([text])
    return embeddings[0] if embeddings else []
