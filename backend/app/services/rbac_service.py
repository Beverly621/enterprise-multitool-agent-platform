from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Permission, Role
from app.schemas.auth import RoleCreate, RoleRead


def serialize_role(role: Role) -> RoleRead:
    return RoleRead(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=sorted(permission.code for permission in role.permissions),
    )


def get_or_create_permission(db: Session, code: str, description: str | None = None) -> Permission:
    permission = db.scalar(select(Permission).where(Permission.code == code))
    if permission:
        return permission
    permission = Permission(code=code, description=description)
    db.add(permission)
    db.flush()
    return permission


def create_role(db: Session, payload: RoleCreate) -> Role:
    role = db.scalar(select(Role).where(Role.name == payload.name))
    if role is None:
        role = Role(name=payload.name, description=payload.description)
        db.add(role)
        db.flush()
    role.description = payload.description
    for code in payload.permissions:
        permission = get_or_create_permission(db, code)
        if permission not in role.permissions:
            role.permissions.append(permission)
    db.commit()
    db.refresh(role)
    return role


def assign_permissions(db: Session, role_name: str, permission_codes: list[str]) -> Role | None:
    role = db.scalar(select(Role).where(Role.name == role_name))
    if role is None:
        return None
    for code in permission_codes:
        permission = get_or_create_permission(db, code)
        if permission not in role.permissions:
            role.permissions.append(permission)
    db.commit()
    db.refresh(role)
    return role

