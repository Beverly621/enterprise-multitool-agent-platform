def parse_document_content(filename: str, content: bytes) -> str:
    return content.decode("utf-8", errors="ignore") if filename else ""

