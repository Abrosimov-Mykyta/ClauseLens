import json
from typing import Any
from urllib import error, request

from app.core.config import settings

ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "red_flags": {"type": "string"},
        "obligations": {"type": "string"},
        "follow_up_questions": {"type": "string"},
    },
    "required": ["summary", "red_flags", "obligations", "follow_up_questions"],
    "additionalProperties": False,
}


def build_fallback_analysis(filename: str, document_text: str) -> dict[str, str]:
    excerpt = " ".join(document_text.split())[:500]
    if not excerpt:
        excerpt = "No extracted text was available, so the document still needs parser attention."

    return {
        "summary": (
            f"Fallback analysis for {filename}: the document has been ingested, and the current "
            f"local parser extracted the following preview: {excerpt}"
        ),
        "red_flags": (
            "Review change-of-control language, indemnity scope, termination mechanics, renewal "
            "windows, and any open-ended liability wording."
        ),
        "obligations": (
            "Capture payment obligations, confidentiality survival, notice periods, approval "
            "rights, and assignment restrictions."
        ),
        "follow_up_questions": (
            "Does this document create unbounded liability, unusual renewal behavior, approval "
            "bottlenecks, or assignment restrictions that could slow a transaction?"
        ),
    }


def _extract_response_text(payload: dict[str, Any]) -> str:
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue

        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"]

    raise ValueError("No output_text content returned from OpenAI response")


def analyze_with_openai(filename: str, document_text: str) -> dict[str, str]:
    if not settings.openai_api_key:
        return build_fallback_analysis(filename, document_text)

    prompt = (
        "You are an AI due diligence analyst. Review the document text and return a compact "
        "JSON object with a business-ready summary, key red flags, key obligations, and "
        "follow-up questions for a reviewer."
    )

    body = {
        "model": settings.openai_model,
        "instructions": prompt,
        "input": [
            {
                "role": "user",
                "content": (
                    f"Filename: {filename}\n\n"
                    "Document text follows. If the text is partial or messy, still produce the "
                    "best structured diligence output you can.\n\n"
                    f"{document_text[:18000]}"
                ),
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "due_diligence_analysis",
                "strict": True,
                "schema": ANALYSIS_SCHEMA,
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
    except (error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return build_fallback_analysis(filename, document_text)

    try:
        parsed_text = _extract_response_text(response_payload)
        parsed_payload = json.loads(parsed_text)
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return build_fallback_analysis(filename, document_text)

    return {
        "summary": parsed_payload.get("summary", ""),
        "red_flags": parsed_payload.get("red_flags", ""),
        "obligations": parsed_payload.get("obligations", ""),
        "follow_up_questions": parsed_payload.get("follow_up_questions", ""),
    }
