from app.tasks.celery_app import celery_app


@celery_app.task(name="documents.parse")
def parse_document(document_id: int) -> dict:
    return {"document_id": document_id, "status": "queued"}

