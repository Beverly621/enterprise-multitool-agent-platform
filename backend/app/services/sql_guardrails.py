import re
from dataclasses import dataclass

import sqlparse

from app.services.schema_reader import allowed_table_names

FORBIDDEN_KEYWORDS = {
    "alter",
    "create",
    "delete",
    "drop",
    "grant",
    "insert",
    "revoke",
    "truncate",
    "update",
}
SENSITIVE_TABLES = {
    "agent_traces",
    "audit_logs",
    "documents",
    "document_chunks",
    "permissions",
    "role_permissions",
    "roles",
    "user_roles",
    "users",
}
SENSITIVE_FIELDS = {
    "address",
    "api_key",
    "email",
    "password",
    "password_hash",
    "phone",
    "secret",
    "token",
}
MAX_LIMIT = 100


@dataclass(slots=True)
class SQLGuardrailResult:
    safe: bool
    sql: str | None
    reason: str | None = None


def validate_sql(sql: str) -> SQLGuardrailResult:
    raw_sql = sql.strip()
    if not raw_sql:
        return SQLGuardrailResult(False, None, "SQL is empty.")

    statements = [statement for statement in sqlparse.parse(raw_sql) if str(statement).strip()]
    if len(statements) != 1:
        return SQLGuardrailResult(False, None, "Multiple SQL statements are not allowed.")

    statement = statements[0]
    statement_type = statement.get_type().upper()
    if statement_type != "SELECT":
        return SQLGuardrailResult(False, None, "Only SELECT statements are allowed.")

    normalized = _strip_trailing_semicolon(raw_sql)
    if ";" in normalized:
        return SQLGuardrailResult(False, None, "Multiple SQL statements are not allowed.")

    lowered = normalized.lower()
    if any(re.search(rf"\b{keyword}\b", lowered) for keyword in FORBIDDEN_KEYWORDS):
        return SQLGuardrailResult(False, None, "Dangerous SQL keyword is not allowed.")

    if re.search(r"select\s+\*", lowered) or re.search(r",\s*\*", lowered):
        return SQLGuardrailResult(False, None, "SELECT * is not allowed.")

    tables = _extract_table_names(lowered)
    if not tables:
        return SQLGuardrailResult(False, None, "Query must reference an allowed demo table.")

    if forbidden := sorted(tables & SENSITIVE_TABLES):
        return SQLGuardrailResult(
            False,
            None,
            f"Sensitive table access blocked: {', '.join(forbidden)}.",
        )

    allowed_tables = allowed_table_names()
    if disallowed := sorted(tables - allowed_tables):
        return SQLGuardrailResult(
            False,
            None,
            f"Only demo business tables are allowed: {', '.join(disallowed)}.",
        )

    if sensitive_fields := sorted(_extract_sensitive_fields(lowered)):
        return SQLGuardrailResult(
            False,
            None,
            f"Sensitive field access blocked: {', '.join(sensitive_fields)}.",
        )

    return SQLGuardrailResult(True, _normalize_limit(normalized), None)


def _strip_trailing_semicolon(sql: str) -> str:
    return sql.rstrip().removesuffix(";").strip()


def _extract_table_names(sql: str) -> set[str]:
    tables = set()
    for match in re.finditer(r"\b(?:from|join)\s+([a-zA-Z_][\w.]*)", sql):
        table = match.group(1).split(".")[-1].strip('"')
        tables.add(table)
    return tables


def _extract_sensitive_fields(sql: str) -> set[str]:
    fields = set()
    select_match = re.search(r"\bselect\b(?P<select>.*?)\bfrom\b", sql, flags=re.DOTALL)
    if not select_match:
        return fields
    selected = select_match.group("select")
    for field in SENSITIVE_FIELDS:
        if re.search(rf"(^|[\s,.(])(?:\w+\.)?{field}($|[\s,).])", selected):
            fields.add(field)
    return fields


def _normalize_limit(sql: str) -> str:
    limit_match = re.search(r"\blimit\s+(\d+)\b", sql, flags=re.IGNORECASE)
    if not limit_match:
        return f"{sql} LIMIT {MAX_LIMIT}"
    limit = min(int(limit_match.group(1)), MAX_LIMIT)
    return re.sub(r"\blimit\s+\d+\b", f"LIMIT {limit}", sql, flags=re.IGNORECASE)
