from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from urllib import request

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "apps" / "api"))
sys.path.insert(0, str(repo_root / "apps" / "worker"))

from app.core.db import SessionLocal
from app.services.auth import get_user_by_access_token
from app.services.persistence import get_workspace_document_payload
from worker import process_next_queued_document


BASE_URL = "http://127.0.0.1:8000"


def send_json(path: str, payload: dict, *, token: str | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method="POST")
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def send_get(path: str, *, token: str) -> dict | list:
    headers = {"Authorization": f"Bearer {token}"}
    req = request.Request(f"{BASE_URL}{path}", headers=headers, method="GET")
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def upload_file(path: str, workspace_id: str, file_path: Path, *, token: str) -> dict:
    boundary = f"----ClauseLensSmoke{int(time.time())}"
    file_bytes = file_path.read_bytes()
    parts = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="workspace_id"\r\n\r\n',
        workspace_id.encode(),
        b"\r\n",
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'.encode(),
        b"Content-Type: text/plain\r\n\r\n",
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    body = b"".join(parts)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    req = request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method="POST")
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    tmp_file = Path("/tmp/clauselens-smoke.txt")
    tmp_file.write_text(
        "Master Services Agreement\n"
        "Termination requires 30 days notice.\n"
        "Vendor may change pricing with 5 days notice.\n"
        "Customer indemnifies vendor broadly.\n",
        encoding="utf-8",
    )

    email = f"qa-{int(time.time())}@example.com"
    register = send_json(
        "/api/auth/register",
        {
            "full_name": "QA Reviewer",
            "email": email,
            "password": "password123",
        },
    )
    member_token = register["access_token"]
    with SessionLocal() as session:
        member_viewer = get_user_by_access_token(session, member_token)
        if member_viewer is None:
            raise RuntimeError("Registered member session was not created")
        member_user, _ = member_viewer

    before_workspaces = send_get("/api/workspaces", token=member_token)
    created_workspace = send_json(
        "/api/workspaces",
        {
            "name": "QA Private Review",
            "description": "Smoke test diligence workspace for ownership and upload verification.",
        },
        token=member_token,
    )
    workspace_id = created_workspace["id"]
    uploaded = upload_file("/api/documents/upload", workspace_id, tmp_file, token=member_token)
    worker_result = None

    if uploaded.get("status") != "ready":
        worker_result = process_next_queued_document()

    workspace_detail = send_get(f"/api/workspaces/{workspace_id}", token=member_token)
    document_id = uploaded["id"]
    with SessionLocal() as session:
        document_payload = get_workspace_document_payload(
            session,
            workspace_id,
            document_id,
            actor=member_user,
        )
    chatted = send_json(
        f"/api/workspaces/{workspace_id}/chat",
        {"question": "What looks risky here?"},
        token=member_token,
    )

    guest = send_json("/api/auth/guest", {})
    guest_token = guest["access_token"]
    guest_workspaces = send_get("/api/workspaces", token=guest_token)

    print(json.dumps(
        {
            "member_initial_workspace_count": len(before_workspaces),
            "created_workspace": created_workspace,
            "upload": uploaded,
            "worker_result": worker_result,
            "chat": {
                "citations": chatted.get("citations", []),
                "answer_preview": chatted.get("answer", "")[:180],
            },
            "workspace_detail_summary": {
                "documents": workspace_detail.get("documents"),
                "retrieval_metrics": workspace_detail.get("retrieval_metrics"),
            },
            "document_detail_summary": {
                "status": document_payload.get("status") if document_payload else None,
                "stage": document_payload.get("stage") if document_payload else None,
                "chunk_count": document_payload.get("retrieval_metrics", {}).get("chunk_count") if document_payload else None,
            },
            "guest_workspace_names": [workspace["name"] for workspace in guest_workspaces],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
