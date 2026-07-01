from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import require_permissions
from app.models.user import User
from app.services.auth_service import serialize_user

router = APIRouter()


@router.get("")
def list_users(
    _: Annotated[User, Depends(require_permissions("users:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    users = db.scalars(select(User).order_by(User.id)).all()
    return ok([serialize_user(user).model_dump() for user in users])

