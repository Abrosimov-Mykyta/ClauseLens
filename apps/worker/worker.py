from celery import Celery

celery_app = Celery("clauselens", broker="redis://localhost:6379/0")


@celery_app.task(name="documents.process")
def process_document(document_id: str) -> dict[str, str]:
    return {
        "document_id": document_id,
        "status": "processed",
    }

