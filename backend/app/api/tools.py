from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.tool import ToolInvokeRequest, ToolRegisterRequest
from app.services.tool_executor import invoke_tool, serialize_tool_call
from app.services.tool_permission_service import require_admin
from app.services.tool_registry import ToolRegistry, serialize_tool

router = APIRouter()


@router.get("")
def list_tools(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    include_disabled: bool = False,
):
    registry = ToolRegistry(db)
    registry.sync_builtin_tools()
    db.commit()
    tools = registry.list_tools(include_disabled=include_disabled)
    return ok([serialize_tool(tool) for tool in tools])


@router.get("/{tool_name}")
def get_tool(
    tool_name: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    registry = ToolRegistry(db)
    registry.sync_builtin_tools()
    db.commit()
    tool = registry.get_tool_record(tool_name)
    if tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return ok(serialize_tool(tool))


@router.post("/register")
def register_tool(
    payload: ToolRegisterRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    require_admin(current_user)
    registry = ToolRegistry(db)
    tool = registry.register_metadata_tool(payload, current_user)
    db.commit()
    db.refresh(tool)
    return ok(serialize_tool(tool), "tool registered")


@router.post("/{tool_name}/enable")
def enable_tool(
    tool_name: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    require_admin(current_user)
    registry = ToolRegistry(db)
    tool = registry.set_enabled(tool_name, True, current_user)
    db.commit()
    db.refresh(tool)
    return ok(serialize_tool(tool), "tool enabled")


@router.post("/{tool_name}/disable")
def disable_tool(
    tool_name: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    require_admin(current_user)
    registry = ToolRegistry(db)
    tool = registry.set_enabled(tool_name, False, current_user)
    db.commit()
    db.refresh(tool)
    return ok(serialize_tool(tool), "tool disabled")


@router.post("/{tool_name}/invoke")
async def invoke_tool_api(
    tool_name: str,
    payload: ToolInvokeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    tool_call = await invoke_tool(
        db=db,
        user=current_user,
        tool_name=tool_name,
        args=payload.args,
        run_id=payload.run_id,
        step_id=payload.step_id,
        session_id=payload.session_id,
    )
    result = serialize_tool_call(tool_call)
    approval_id = None
    if tool_call.tool_result:
        approval_id = tool_call.tool_result.get("approval_id")
    return ok(
        {
            "tool_call_id": tool_call.tool_call_id,
            "tool_name": tool_call.tool_name,
            "status": tool_call.status,
            "result": result["tool_result"],
            "approval_id": approval_id,
            "error_message": tool_call.error_message,
        }
    )
