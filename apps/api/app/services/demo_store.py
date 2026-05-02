WORKSPACES = [
    {
        "id": "ws-acme",
        "name": "Acme Acquisition Review",
        "status": "ready",
        "documents": 14,
        "risks": 6,
    },
    {
        "id": "ws-northstar",
        "name": "Northstar Vendor Audit",
        "status": "processing",
        "documents": 5,
        "risks": 2,
    },
]


def list_workspaces() -> list[dict]:
    return WORKSPACES


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

