from app.tasks.celery_app import celery_app


@celery_app.task(name="reports.generate")
def generate_report(run_id: str) -> dict:
    return {"run_id": run_id, "status": "queued"}

