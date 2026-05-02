import argparse
import time

from app.core.config import settings
from app.core.db import SessionLocal
from app.services.document_processing import process_document
from app.services.persistence import claim_next_document_for_processing


def process_next_queued_document() -> dict[str, str] | None:
    with SessionLocal() as session:
        document = claim_next_document_for_processing(session)
        if document is None:
            return None

        return process_document(session, document.id)


def run_worker(*, once: bool = False) -> None:
    while True:
        result = process_next_queued_document()
        if result:
            print(
                f"[worker] processed document={result['document_id']} "
                f"status={result['status']} stage={result['stage']}"
            )
        elif once:
            return

        if once:
            return

        time.sleep(settings.worker_poll_interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="ClauseLens document worker")
    parser.add_argument("--once", action="store_true", help="Process at most one queued document")
    args = parser.parse_args()
    run_worker(once=args.once)


if __name__ == "__main__":
    main()
