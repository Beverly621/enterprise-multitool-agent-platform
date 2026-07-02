import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(slots=True)
class SQLExecutionResult:
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    duration_ms: int
    error: str | None = None


def execute_safe_sql(db: Session, sql: str, max_rows: int = 100) -> SQLExecutionResult:
    started = time.perf_counter()
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(text("SET LOCAL TRANSACTION READ ONLY"))
        db.execute(text("SET LOCAL statement_timeout = 5000"))

    try:
        result = db.execute(text(sql))
        rows = [dict(row._mapping) for row in result.fetchmany(max_rows)]
        duration_ms = int((time.perf_counter() - started) * 1000)
        columns = list(result.keys())
        return SQLExecutionResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        return SQLExecutionResult(
            columns=[],
            rows=[],
            row_count=0,
            duration_ms=duration_ms,
            error=str(exc),
        )
