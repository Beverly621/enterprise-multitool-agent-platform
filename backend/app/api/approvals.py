from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.approval import ApprovalDecisionRequest
from app.services.approval_service import (
    approve_request,
    get_approval,
    list_approvals,
    reject_request,
    serialize_approval,
)

router = APIRouter()


@router.get("")
def approvals(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok([serialize_approval(item) for item in list_approvals(db, current_user)])


@router.get("/{approval_id}")
def approval_detail(
    approval_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(serialize_approval(get_approval(db, approval_id, current_user)))


@router.post("/{approval_id}/approve")
def approve(
    approval_id: str,
    payload: ApprovalDecisionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(serialize_approval(approve_request(db, approval_id, current_user, payload.reason)))


@router.post("/{approval_id}/reject")
def reject(
    approval_id: str,
    payload: ApprovalDecisionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(serialize_approval(reject_request(db, approval_id, current_user, payload.reason)))
