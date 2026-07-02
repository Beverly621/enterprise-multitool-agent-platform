from fastapi import APIRouter

from app.api import auth, chat, documents, knowledge_base, roles, sql_agent, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, tags=["rbac"])
api_router.include_router(knowledge_base.router, prefix="/kb", tags=["knowledge-base"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(sql_agent.router, prefix="/sql-agent", tags=["sql-agent"])
