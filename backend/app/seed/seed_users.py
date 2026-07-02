from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.rbac import Permission, Role
from app.models.user import User

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "Admin": [
        "admin:*",
        "users:read",
        "roles:read",
        "roles:write",
        "permissions:assign",
        "audit:read",
    ],
    "Developer": ["sql_agent:execute", "tools:register", "traces:read", "kb:read", "tools:execute"],
    "User": ["kb:read", "kb:chat", "reports:generate", "tools:execute"],
    "Guest": ["kb:read_public"],
}

DEMO_USERS = [
    ("admin@example.com", "admin123", "Admin User", "Admin", True),
    ("developer@example.com", "dev123", "Developer User", "Developer", False),
    ("user@example.com", "user123", "Demo User", "User", False),
    ("guest@example.com", "guest123", "Guest User", "Guest", False),
]


def get_or_create_permission(db, code: str) -> Permission:
    permission = db.scalar(select(Permission).where(Permission.code == code))
    if permission:
        return permission
    permission = Permission(code=code, description=f"Permission: {code}")
    db.add(permission)
    db.flush()
    return permission


def get_or_create_role(db, name: str) -> Role:
    role = db.scalar(select(Role).where(Role.name == name))
    if role:
        return role
    role = Role(name=name, description=f"{name} role")
    db.add(role)
    db.flush()
    return role


def seed() -> None:
    with SessionLocal() as db:
        roles: dict[str, Role] = {}
        for role_name, permissions in ROLE_PERMISSIONS.items():
            role = get_or_create_role(db, role_name)
            for code in permissions:
                permission = get_or_create_permission(db, code)
                if permission not in role.permissions:
                    role.permissions.append(permission)
            roles[role_name] = role

        for email, password, full_name, role_name, is_superuser in DEMO_USERS:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(
                    email=email,
                    full_name=full_name,
                    hashed_password=hash_password(password),
                    is_superuser=is_superuser,
                    roles=[roles[role_name]],
                )
                db.add(user)
            elif roles[role_name] not in user.roles:
                user.roles.append(roles[role_name])

        db.commit()
        print("Seeded users, roles and permissions.")


if __name__ == "__main__":
    seed()
