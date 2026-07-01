READ_ONLY_PREFIXES = ("select", "with")


def is_read_only_sql(sql: str) -> bool:
    return sql.strip().lower().startswith(READ_ONLY_PREFIXES)

