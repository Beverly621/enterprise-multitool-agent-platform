from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.document import Document
from app.models.user import User
from app.services.kb_permissions import get_accessible_kb

router = APIRouter()


@router.get("/{document_id}")
def get_document(
    document_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    get_accessible_kb(db, document.kb_id, current_user)
    return ok(
        {
            "id": document.id,
            "kb_id": document.kb_id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_path": document.file_path,
            "status": document.status,
            "chunk_count": document.chunk_count,
            "error_message": document.error_message,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
        }
    )
