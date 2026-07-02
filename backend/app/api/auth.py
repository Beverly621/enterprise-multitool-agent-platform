from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.services.auth_service import authenticate_user, issue_token, register_user, serialize_user

router = APIRouter()


@router.post("/register")
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    user = register_user(db, payload)
    return ok(serialize_user(user).model_dump(), "registered")


@router.post("/login")
def login(payload: UserLogin, db: Annotated[Session, Depends(get_db)]):
    user = authenticate_user(db, payload.email, payload.password)
    db.add(
        AuditLog(
            actor_id=user.id,
            action="LOGIN",
            resource_type="user",
            resource_id=str(user.id),
            metadata_json={"email": user.email},
        )
    )
    db.commit()
    return ok(issue_token(user).model_dump(), "logged in")


@router.get("/me")
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return ok(serialize_user(current_user).model_dump())
