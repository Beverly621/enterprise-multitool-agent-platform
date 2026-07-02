from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.models.user import User


@dataclass(frozen=True, slots=True)
class ToolMetadata:
    name: str
    description: str
    schema_json: dict[str, Any]
    permission_level: str = "User"
    require_approval: bool = False
    timeout_ms: int = 5000
    retry_count: int = 1


@dataclass(slots=True)
class ToolContext:
    db: Session
    user: User
    run_id: str | None = None
    step_id: int | None = None
    session_id: str | None = None


class BaseTool(Protocol):
    metadata: ToolMetadata

    async def execute(self, args: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        """Execute a whitelisted tool implementation."""
