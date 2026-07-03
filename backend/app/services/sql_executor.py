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
    try:
        bind = db.get_bind()
        if bind is not None and bind.dialect.name == "postgresql":
            with bind.connect() as connection:
                with connection.begin():
                    connection.execute(text("SET LOCAL TRANSACTION READ ONLY"))
                    connection.execute(text("SET LOCAL statement_timeout = 5000"))
                    result = connection.execute(text(sql))
                    rows = [dict(row._mapping) for row in result.fetchmany(max_rows)]
                    columns = list(result.keys())
        else:
            result = db.execute(text(sql))
            rows = [dict(row._mapping) for row in result.fetchmany(max_rows)]
            columns = list(result.keys())
        duration_ms = int((time.perf_counter() - started) * 1000)
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
