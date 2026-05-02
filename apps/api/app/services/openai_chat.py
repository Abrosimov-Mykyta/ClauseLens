import json
from typing import Any
from urllib import error, request

from app.core.config import settings

CHAT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "citations": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["answer", "citations"],
    "additionalProperties": False,
}


def build_fallback_chat_answer(
    question: str,
    workspace_name: str,
    contexts: list[dict[str, str]],
) -> dict[str, list[str] | str]:
    top_contexts = contexts[:3]
    if not top_contexts:
        return {
            "answer": (
                f"ClauseLens does not have enough indexed material yet to answer '{question}' "
                f"for {workspace_name}. Upload more documents or generate analysis first."
            ),
            "citations": [],
        }

    bullets = []
    citations = []
    for context in top_contexts:
        citations.append(context["citation"])
        bullets.append(f"{context['label']}: {context['content'][:220]}")

    answer = (
        f"For {workspace_name}, the strongest grounded signals related to '{question}' are: "
        + " ".join(bullets)
    )

    return {
        "answer": answer,
        "citations": citations,
    }


def _extract_response_text(payload: dict[str, Any]) -> str:
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue

        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"]

    raise ValueError("No output_text content returned from OpenAI response")


def answer_with_openai(
    question: str,
    workspace_name: str,
    contexts: list[dict[str, str]],
) -> dict[str, list[str] | str]:
    if not settings.openai_api_key:
        return build_fallback_chat_answer(question, workspace_name, contexts)

    rendered_context = "\n\n".join(
        [
            f"[{index + 1}] citation={context['citation']} label={context['label']}\n{context['content']}"
            for index, context in enumerate(contexts[:8])
        ]
    )

    body = {
        "model": settings.openai_model,
        "instructions": (
            "You are an AI due diligence reviewer. Answer only from the provided workspace "
            "context. If evidence is limited, say so clearly. Return compact JSON."
        ),
        "input": [
            {
                "role": "user",
                "content": (
                    f"Workspace: {workspace_name}\n"
                    f"Reviewer question: {question}\n\n"
                    "Use only the context below. Prefer the strongest and most directly relevant "
                    "evidence. Always include citation labels that match the provided context.\n\n"
                    f"{rendered_context}"
                ),
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "grounded_due_diligence_answer",
                "strict": True,
                "schema": CHAT_SCHEMA,
            }
        },
    }

    http_request = request.Request(
        settings.openai_base_url,
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
        parsed_text = _extract_response_text(response_payload)
        parsed_payload = json.loads(parsed_text)
    except (error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError, ValueError, KeyError, TypeError):
        return build_fallback_chat_answer(question, workspace_name, contexts)

    citations = parsed_payload.get("citations", [])
    if not isinstance(citations, list):
        citations = []

    return {
        "answer": parsed_payload.get("answer", ""),
        "citations": [str(citation) for citation in citations],
    }
