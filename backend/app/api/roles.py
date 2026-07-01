from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import require_permissions
from app.models.rbac import Role
from app.models.user import User
from app.schemas.auth import PermissionAssign, RoleCreate
from app.services.rbac_service import assign_permissions, create_role, serialize_role

router = APIRouter()


@router.get("/roles")
def list_roles(
    _: Annotated[User, Depends(require_permissions("roles:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    roles = db.scalars(select(Role).order_by(Role.id)).all()
    return ok([serialize_role(role).model_dump() for role in roles])


@router.post("/roles")
def add_role(
    payload: RoleCreate,
    _: Annotated[User, Depends(require_permissions("roles:write"))],
    db: Annotated[Session, Depends(get_db)],
):
    role = create_role(db, payload)
    return ok(serialize_role(role).model_dump(), "role saved")


@router.post("/permissions/assign")
def assign_role_permissions(
    payload: PermissionAssign,
    _: Annotated[User, Depends(require_permissions("permissions:assign"))],
    db: Annotated[Session, Depends(get_db)],
):
    role = assign_permissions(db, payload.role_name, payload.permission_codes)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return ok(serialize_role(role).model_dump(), "permissions assigned")

