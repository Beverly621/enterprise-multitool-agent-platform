from app.services.chunk_service import chunk_text


def test_chunk_text_prefers_paragraphs_and_metadata() -> None:
    text = "Alpha paragraph.\n\nBeta paragraph is a little longer.\n\nGamma paragraph."
    chunks = chunk_text(text, chunk_size=45, overlap=5, base_metadata={"source": "unit"})

    assert len(chunks) >= 2
    assert chunks[0].chunk_index == 0
    assert chunks[0].metadata["source"] == "unit"
    assert "Alpha paragraph" in chunks[0].content

