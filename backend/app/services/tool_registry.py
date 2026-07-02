from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.tool import AgentTool
from app.models.user import User
from app.schemas.tool import ToolRegisterRequest
from app.services.tool_validation_service import ToolValidationError, validate_tool_schema
from app.tools import BaseTool, get_builtin_tools


def normalize_tool_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


class ToolRegistry:
    def __init__(self, db: Session):
        self.db = db
        self._builtin_tools = get_builtin_tools()

    @property
    def builtin_tools(self) -> dict[str, BaseTool]:
        return self._builtin_tools

    def sync_builtin_tools(self) -> list[AgentTool]:
        synced: list[AgentTool] = []
        for tool in self._builtin_tools.values():
            metadata = tool.metadata
            db_tool = self.db.scalar(select(AgentTool).where(AgentTool.name == metadata.name))
            if db_tool is None:
                db_tool = AgentTool(
                    name=metadata.name,
                    endpoint=f"builtin://{metadata.name}",
                    is_active=True,
                    enabled=True,
                )
                self.db.add(db_tool)
            db_tool.description = metadata.description
            db_tool.schema_json = metadata.schema_json
            db_tool.permission_level = metadata.permission_level
            db_tool.require_approval = metadata.require_approval
            db_tool.requires_approval = metadata.require_approval
            db_tool.timeout_ms = metadata.timeout_ms
            db_tool.retry_count = metadata.retry_count
            synced.append(db_tool)
        self.db.flush()
        return synced

    def list_tools(self, include_disabled: bool = False) -> list[AgentTool]:
        statement = select(AgentTool).order_by(AgentTool.name)
        if not include_disabled:
            statement = statement.where(AgentTool.enabled.is_(True), AgentTool.is_active.is_(True))
        return list(self.db.scalars(statement).all())

    def get_tool_record(self, tool_name: str) -> AgentTool | None:
        return self.db.scalar(
            select(AgentTool).where(AgentTool.name == normalize_tool_name(tool_name))
        )

    def get_builtin(self, tool_name: str) -> BaseTool | None:
        return self._builtin_tools.get(normalize_tool_name(tool_name))

    def register_metadata_tool(self, payload: ToolRegisterRequest, actor: User) -> AgentTool:
        name = normalize_tool_name(payload.name)
        try:
            validate_tool_schema(payload.tool_schema)
        except ToolValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        if name in self._builtin_tools and payload.endpoint and not payload.endpoint.startswith("builtin://"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Built-in tool names are reserved",
            )
        db_tool = self.get_tool_record(name)
        if db_tool is None:
            db_tool = AgentTool(name=name, created_by=actor.id, enabled=True, is_active=True)
            self.db.add(db_tool)
            action = "TOOL_REGISTERED"
        else:
            action = "TOOL_UPDATED"
        db_tool.description = payload.description
        db_tool.schema_json = payload.tool_schema
        db_tool.endpoint = payload.endpoint or f"metadata://{name}"
        db_tool.permission_level = payload.permission_level
        db_tool.require_approval = payload.require_approval
        db_tool.requires_approval = payload.require_approval
        db_tool.timeout_ms = payload.timeout_ms
        db_tool.retry_count = payload.retry_count
        self.db.add(
            AuditLog(
                actor_id=actor.id,
                action=action,
                resource_type="agent_tool",
                resource_id=name,
                metadata_json={"permission_level": payload.permission_level},
            )
        )
        self.db.flush()
        return db_tool

    def set_enabled(self, tool_name: str, enabled: bool, actor: User) -> AgentTool:
        db_tool = self.get_tool_record(tool_name)
        if db_tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
        db_tool.enabled = enabled
        db_tool.is_active = enabled
        self.db.add(
            AuditLog(
                actor_id=actor.id,
                action="TOOL_ENABLED" if enabled else "TOOL_DISABLED",
                resource_type="agent_tool",
                resource_id=db_tool.name,
            )
        )
        self.db.flush()
        return db_tool


def serialize_tool(tool: AgentTool) -> dict[str, Any]:
    return {
        "id": tool.id,
        "name": tool.name,
        "description": tool.description,
        "schema_json": tool.schema_json,
        "permission_level": tool.permission_level,
        "require_approval": tool.require_approval or tool.requires_approval,
        "timeout_ms": tool.timeout_ms,
        "retry_count": tool.retry_count,
        "enabled": tool.enabled and tool.is_active,
        "created_at": tool.created_at,
        "updated_at": tool.updated_at,
    }
