def route_intent(query: str) -> str:
    lowered = query.lower()
    if "sql" in lowered or "database" in lowered:
        return "sql"
    if "tool" in lowered:
        return "tool"
    return "rag"

