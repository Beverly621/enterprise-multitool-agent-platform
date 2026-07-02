from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.cleanup_expired")
def cleanup_expired_task_metadata() -> dict:
    return {"status": "not_implemented", "message": "Cleanup scheduling is reserved."}
