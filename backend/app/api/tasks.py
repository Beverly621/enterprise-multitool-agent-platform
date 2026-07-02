from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.task_progress import TaskProgress
from app.models.user import User
from app.services.task_progress_service import serialize_task_progress
from app.services.tool_permission_service import highest_role_level

router = APIRouter()


@router.get("")
def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 100,
):
    limit = min(max(limit, 1), 500)
    statement = select(TaskProgress).order_by(TaskProgress.id.desc()).limit(limit)
    if highest_role_level(current_user) < 3:
        statement = statement.where(TaskProgress.user_id == current_user.id)
    tasks = db.scalars(statement).all()
    return ok([serialize_task_progress(task) for task in tasks])
