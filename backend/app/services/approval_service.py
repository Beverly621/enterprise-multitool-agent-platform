def requires_human_approval(action: str) -> bool:
    return action in {"refund_request", "external_write", "sql_write"}

