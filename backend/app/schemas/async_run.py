from pydantic import BaseModel


class AsyncAgentRunResponse(BaseModel):
    run_id: str
    task_id: str
    status: str
    message: str
    progress_url: str
    trace_url: str
    idempotent: bool = False


class CancelTaskResponse(BaseModel):
    run_id: str | None = None
    task_id: str
    status: str
    message: str
