from datetime import datetime

from pydantic import BaseModel


class TaskProgressResponse(BaseModel):
    run_id: str | None = None
    task_id: str
    task_type: str
    status: str
    progress: int
    current_stage: str | None = None
    message: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    updated_at: datetime
    finished_at: datetime | None = None
