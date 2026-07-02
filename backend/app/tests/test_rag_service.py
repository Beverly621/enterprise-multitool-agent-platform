from app.schemas.kb import Citation, RAGResponse, RetrievedChunk, SearchResponse


def test_rag_response_schema_contains_required_fields() -> None:
    response = RAGResponse(
        answer="Answer",
        citations=[
            Citation(
                document_id=1,
                filename="demo.md",
                chunk_id=10,
                chunk_index=0,
                score=0.9,
            )
        ],
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id=10,
                document_id=1,
                filename="demo.md",
                chunk_index=0,
                content="Context",
                score=0.9,
            )
        ],
        run_id="rag_test",
    )

    assert response.answer == "Answer"
    assert response.citations[0].filename == "demo.md"
    assert response.retrieved_chunks[0].content == "Context"
    assert response.run_id == "rag_test"


def test_search_response_keeps_results_for_api_compatibility() -> None:
    response = SearchResponse(
        query="policy",
        top_k=1,
        retrieved_chunks=[],
        citations=[],
        results=[
            {
                "content": "Employees disclose conflicts.",
                "score": 0.99,
                "source": {"document_id": 1, "filename": "policy.md", "chunk_index": 0},
            }
        ],
    )

    assert response.results[0]["source"]["filename"] == "policy.md"
