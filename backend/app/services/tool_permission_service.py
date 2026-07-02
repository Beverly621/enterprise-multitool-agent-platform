from fastapi import HTTPException, status

from app.core.security import get_user_permissions
from app.models.tool import AgentTool
from app.models.user import User

ROLE_LEVELS = {"Guest": 0, "User": 1, "Developer": 2, "Admin": 3}


def highest_role_level(user: User) -> int:
    if "admin:*" in get_user_permissions(user):
        return ROLE_LEVELS["Admin"]
    return max((ROLE_LEVELS.get(role.name, 0) for role in user.roles), default=ROLE_LEVELS["Guest"])


def can_invoke_tool(user: User, tool: AgentTool) -> bool:
    required = ROLE_LEVELS.get(tool.permission_level or "User", ROLE_LEVELS["User"])
    return highest_role_level(user) >= required


def require_tool_access(user: User, tool: AgentTool) -> None:
    if can_invoke_tool(user, tool):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Tool {tool.name} requires {tool.permission_level} role or higher.",
    )


def require_admin(user: User) -> None:
    if highest_role_level(user) >= ROLE_LEVELS["Admin"]:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")
