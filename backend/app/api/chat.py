from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.kb import RAGRequest
from app.services.kb_permissions import get_accessible_kb
from app.services.rag_service import answer_with_rag

router = APIRouter()


@router.post("/rag")
def rag_chat(
    payload: RAGRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    get_accessible_kb(db, payload.kb_id, current_user)
    response = answer_with_rag(
        db,
        user_id=current_user.id,
        kb_id=payload.kb_id,
        query=payload.query,
        top_k=payload.top_k,
        session_id=payload.session_id,
    )
    return ok(response.model_dump())
