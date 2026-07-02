from app.services.document_parser import parse_document_content


def test_parse_markdown_document() -> None:
    parsed = parse_document_content("demo.md", b"# Title\n\nEnterprise RAG\n\n\nTracing")

    assert "Enterprise RAG" in parsed.text
    assert "\n\n\n" not in parsed.text
    assert parsed.metadata["file_type"] == "md"


def test_parse_csv_document() -> None:
    parsed = parse_document_content("orders.csv", b"order_id,status\nORD-1,shipped\n")

    assert "order_id: ORD-1" in parsed.text
    assert parsed.metadata["row_count"] == 1

