from app.tasks.celery_app import celery_app


@celery_app.task(name="embeddings.build")
def build_embeddings(document_id: int) -> dict:
    return {"document_id": document_id, "status": "queued"}

