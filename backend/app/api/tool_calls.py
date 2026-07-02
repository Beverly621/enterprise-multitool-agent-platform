from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.user import User
from app.services.tool_executor import get_tool_call, serialize_tool_call

router = APIRouter()


@router.get("/{tool_call_id}")
def tool_call_detail(
    tool_call_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(serialize_tool_call(get_tool_call(db, tool_call_id, current_user)))
