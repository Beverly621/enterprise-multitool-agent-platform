from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "enterprise_multitool_agent_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    imports=(
        "app.tasks.agent_tasks",
        "app.tasks.cleanup_tasks",
        "app.tasks.document_tasks",
        "app.tasks.embedding_tasks",
        "app.tasks.report_tasks",
        "app.tasks.retry_tasks",
    ),
)
