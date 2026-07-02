from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolRegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=2, max_length=128, pattern=r"^[a-zA-Z0-9_:-]+$")
    description: str | None = None
    tool_schema: dict[str, Any] = Field(alias="schema_json")
    endpoint: str | None = None
    permission_level: str = Field(default="User", pattern="^(Guest|User|Developer|Admin)$")
    require_approval: bool = False
    timeout_ms: int = Field(default=5000, ge=100, le=60000)
    retry_count: int = Field(default=1, ge=0, le=5)


class ToolInvokeRequest(BaseModel):
    args: dict[str, Any] = Field(default_factory=dict)
    run_id: str | None = None
    step_id: int | None = None
    session_id: str | None = None


class ToolRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    description: str | None
    tool_schema: dict[str, Any] = Field(alias="schema_json")
    permission_level: str
    require_approval: bool
    timeout_ms: int
    retry_count: int
    enabled: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ToolCallRead(BaseModel):
    id: int
    tool_call_id: str
    run_id: str | None
    user_id: int | None
    tool_name: str
    tool_args: dict[str, Any] | None
    tool_result: dict[str, Any] | None
    status: str
    duration_ms: int | None
    requires_approval: bool
    approval_id: int | None
    error_message: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ToolInvokeResponse(BaseModel):
    tool_call_id: str
    tool_name: str
    status: str
    result: dict[str, Any] | None = None
    approval_id: str | None = None
    error_message: str | None = None
