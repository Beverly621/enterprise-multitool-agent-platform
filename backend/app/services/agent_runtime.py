from sqlalchemy.orm import Session

from app.agent.runtime import response_from_state, run_agent_chat
from app.models.user import User


async def run_agent(
    db: Session,
    user: User,
    query: str,
    session_id: str | None = None,
    kb_id: int | None = None,
) -> dict:
    state = await run_agent_chat(db, user, query, session_id=session_id, kb_id=kb_id)
    return response_from_state(state)
