from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.agent_chat import AgentChatRequest
from app.services.agent_runtime import run_agent

router = APIRouter()


@router.post("/chat")
async def agent_chat(
    payload: AgentChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    response = await run_agent(
        db,
        current_user,
        query=payload.query,
        session_id=payload.session_id,
        kb_id=payload.kb_id,
    )
    return ok(response)
