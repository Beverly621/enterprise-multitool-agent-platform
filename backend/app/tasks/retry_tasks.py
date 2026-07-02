from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.retry_failed")
def retry_failed_tasks() -> dict:
    return {"status": "not_implemented", "message": "Manual retry workflow is reserved."}
