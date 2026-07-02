from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.tool import ToolCall
from app.models.user import User
from app.services.tool_executor import get_tool_call, serialize_tool_call
from app.services.tool_permission_service import highest_role_level

router = APIRouter()


@router.get("")
def list_tool_calls(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 100,
):
    limit = min(max(limit, 1), 500)
    statement = select(ToolCall).order_by(ToolCall.id.desc()).limit(limit)
    if highest_role_level(current_user) < 3:
        statement = statement.where(ToolCall.user_id == current_user.id)
    return ok([serialize_tool_call(item) for item in db.scalars(statement).all()])


@router.get("/{tool_call_id}")
def tool_call_detail(
    tool_call_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(serialize_tool_call(get_tool_call(db, tool_call_id, current_user)))
