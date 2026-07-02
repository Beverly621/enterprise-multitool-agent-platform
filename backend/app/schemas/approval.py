from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ApprovalDecisionRequest(BaseModel):
    reason: str | None = None


class ApprovalRead(BaseModel):
    id: int
    approval_id: str
    tool_call_id: str | None
    user_id: int | None
    tool_name: str | None
    approval_type: str | None
    status: str
    reason: str | None
    request_payload: dict[str, Any] | None
    approval_result: dict[str, Any] | None
    requested_by: int | None
    approved_by: int | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None
