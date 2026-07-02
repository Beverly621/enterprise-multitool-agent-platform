from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: int
    report_id: str
    run_id: str | None = None
    user_id: int | None = None
    title: str
    report_type: str
    content_markdown: str
    summary: str | None = None
    source_metadata_json: dict[str, Any] | None = None
    status: str
    created_at: datetime
    updated_at: datetime
