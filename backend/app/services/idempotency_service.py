from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task_progress import IdempotencyKey


def request_hash(payload: dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def get_reusable_idempotency_key(
    db: Session,
    user_id: int,
    idempotency_key: str,
    expected_hash: str,
) -> IdempotencyKey | None:
    item = db.scalar(
        select(IdempotencyKey).where(
            IdempotencyKey.user_id == user_id,
            IdempotencyKey.idempotency_key == idempotency_key,
        )
    )
    if item is None:
        return None
    expires_at = item.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= datetime.now(UTC):
        return None
    if item.request_hash != expected_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency key was already used for a different request.",
        )
    return item


def save_idempotency_key(
    db: Session,
    user_id: int,
    idempotency_key: str,
    request_hash_value: str,
    run_id: str,
    task_id: str,
    status_value: str = "PENDING",
    ttl_hours: int = 24,
) -> IdempotencyKey:
    item = db.scalar(
        select(IdempotencyKey).where(
            IdempotencyKey.user_id == user_id,
            IdempotencyKey.idempotency_key == idempotency_key,
        )
    )
    expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)
    if item is None:
        item = IdempotencyKey(
            user_id=user_id,
            idempotency_key=idempotency_key,
            request_hash=request_hash_value,
            run_id=run_id,
            task_id=task_id,
            status=status_value,
            expires_at=expires_at,
        )
        db.add(item)
    else:
        item.request_hash = request_hash_value
        item.run_id = run_id
        item.task_id = task_id
        item.status = status_value
        item.expires_at = expires_at
    db.flush()
    return item


def update_idempotency_status(
    db: Session,
    task_id: str,
    status_value: str,
) -> None:
    item = db.scalar(select(IdempotencyKey).where(IdempotencyKey.task_id == task_id))
    if item is not None:
        item.status = status_value
        db.flush()
