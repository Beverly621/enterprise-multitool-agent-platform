import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user, get_user_permissions
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.schemas.kb import KnowledgeBaseCreate, SearchRequest
from app.services.kb_permissions import accessible_kb_statement, can_create_kb, get_accessible_kb
from app.services.rag_service import semantic_search
from app.tasks.document_tasks import parse_document

ALLOWED_EXTENSIONS = {"pdf", "docx", "md", "markdown", "txt", "csv"}
UPLOAD_DIR = Path("storage/uploads")

router = APIRouter()


@router.post("")
def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not can_create_kb(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to create KB",
        )
    kb = KnowledgeBase(
        name=payload.name,
        description=payload.description,
        visibility=payload.visibility,
        owner_id=current_user.id,
    )
    db.add(kb)
    db.flush()
    db.add(
        AuditLog(
            actor_id=current_user.id,
            action="KB_CREATE",
            resource_type="knowledge_base",
            resource_id=str(kb.id),
            metadata_json={"name": kb.name, "visibility": kb.visibility},
        )
    )
    db.commit()
    db.refresh(kb)
    return ok(_serialize_kb(kb), "knowledge base created")


@router.get("")
def list_knowledge_bases(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    kbs = db.scalars(accessible_kb_statement(current_user)).all()
    return ok([_serialize_kb(kb) for kb in kbs])


@router.post("/{kb_id}/documents")
async def upload_document(
    kb_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
):
    kb = get_accessible_kb(db, kb_id, current_user)
    if kb.owner_id != current_user.id and "admin:*" not in get_user_permissions(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only KB owner or Admin can upload",
        )

    suffix = Path(file.filename or "").suffix.lower().lstrip(".")
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {suffix}",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{Path(file.filename or 'upload').name}"
    stored_path = UPLOAD_DIR / stored_name
    stored_path.write_bytes(await file.read())

    document = Document(
        kb_id=kb.id,
        filename=file.filename or stored_name,
        file_type=suffix,
        file_path=str(stored_path),
        status="UPLOADED",
    )
    db.add(document)
    db.flush()
    db.add(
        AuditLog(
            actor_id=current_user.id,
            action="DOCUMENT_UPLOAD",
            resource_type="document",
            resource_id=str(document.id),
            metadata_json={"kb_id": kb.id, "filename": document.filename},
        )
    )
    db.commit()
    db.refresh(document)

    queued = True
    try:
        parse_document.delay(document.id)
    except Exception:
        queued = False

    return ok({"document": _serialize_document(document), "queued": queued}, "document uploaded")


@router.post("/{kb_id}/search")
def search_knowledge_base(
    kb_id: int,
    payload: SearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    get_accessible_kb(db, kb_id, current_user)
    result = semantic_search(
        db,
        kb_id=kb_id,
        query=payload.query,
        top_k=payload.top_k,
        metadata_filter=payload.metadata_filter,
    )
    return ok(result.model_dump())


def _serialize_kb(kb: KnowledgeBase) -> dict:
    return {
        "id": kb.id,
        "name": kb.name,
        "description": kb.description,
        "owner_id": kb.owner_id,
        "visibility": kb.visibility,
        "created_at": kb.created_at,
        "updated_at": kb.updated_at,
    }


def _serialize_document(document: Document) -> dict:
    return {
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
