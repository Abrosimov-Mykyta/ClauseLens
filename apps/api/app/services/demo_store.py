WORKSPACES = [
    {
        "id": "ws-acme",
        "name": "Acme Acquisition Review",
        "status": "ready",
        "documents": 14,
        "risks": 6,
        "description": "Cross-document review for a mid-market acquisition data room.",
        "members": 3,
        "recent_activity": [
            "Supplier agreement ingestion finished",
            "Risk analysis refreshed",
            "Reviewer asked three follow-up questions",
        ],
    },
    {
        "id": "ws-northstar",
        "name": "Northstar Vendor Audit",
        "status": "processing",
        "documents": 5,
        "risks": 2,
        "description": "Ongoing procurement review with fresh uploads still parsing.",
        "members": 2,
        "recent_activity": [
            "NDA uploaded",
            "Employment agreement queued for chunking",
            "Audit event stream active",
        ],
    },
]


def list_workspaces() -> list[dict]:
    return WORKSPACES


def get_workspace(workspace_id: str) -> dict | None:
    return next((workspace for workspace in WORKSPACES if workspace["id"] == workspace_id), None)


def list_audit_events(workspace_id: str) -> list[dict]:
    return [
        {
            "id": f"audit-{workspace_id}-1",
            "event_type": "document.uploaded",
            "message": "Uploaded supplier-agreement.pdf",
            "created_at": "2026-05-02T07:15:00Z",
        },
        {
            "id": f"audit-{workspace_id}-2",
            "event_type": "analysis.completed",
            "message": "Generated red flag summary for the latest review batch",
            "created_at": "2026-05-02T07:23:00Z",
        },
        {
            "id": f"audit-{workspace_id}-3",
            "event_type": "chat.question_asked",
            "message": "Reviewer asked about indemnity exposure",
            "created_at": "2026-05-02T07:31:00Z",
        },
    ]


def answer_question(workspace_id: str, question: str) -> dict:
    return {
        "answer": (
            f"Demo answer for {workspace_id}: the assistant would use retrieval over indexed "
            f"chunks before answering '{question}'."
        ),
        "citations": [
            "supplier-agreement.pdf#section-4",
            "share-purchase-agreement.pdf#section-12",
        ],
    }
