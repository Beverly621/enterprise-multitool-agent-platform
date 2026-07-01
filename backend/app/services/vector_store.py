class VectorStore:
    """Placeholder vector store facade for the RAG phase."""

    def search(self, query: str, limit: int = 5) -> list[dict]:
        return [{"query": query, "limit": limit, "status": "planned"}]

