from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import get_user_permissions
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User


def can_access_kb(user: User, kb: KnowledgeBase) -> bool:
    permissions = get_user_permissions(user)
    if "admin:*" in permissions:
        return True
    if kb.visibility == "public":
        return True
    return kb.owner_id == user.id


def can_create_kb(user: User) -> bool:
    permissions = get_user_permissions(user)
    return "admin:*" in permissions or "kb:chat" in permissions


def accessible_kb_statement(user: User):
    permissions = get_user_permissions(user)
    if "admin:*" in permissions:
        return select(KnowledgeBase).order_by(KnowledgeBase.id)
    return (
        select(KnowledgeBase)
        .where(or_(KnowledgeBase.visibility == "public", KnowledgeBase.owner_id == user.id))
        .order_by(KnowledgeBase.id)
    )


def get_accessible_kb(db: Session, kb_id: int, user: User) -> KnowledgeBase:
    kb = db.get(KnowledgeBase, kb_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )
    if not can_access_kb(user, kb):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this knowledge base",
        )
    return kb
