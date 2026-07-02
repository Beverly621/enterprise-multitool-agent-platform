from dataclasses import dataclass, field


@dataclass(slots=True)
class TextChunk:
    chunk_index: int
    content: str
    metadata: dict = field(default_factory=dict)


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
    base_metadata: dict | None = None,
) -> list[TextChunk]:
    cleaned = text.strip()
    if not cleaned:
        return []

    paragraphs = [paragraph.strip() for paragraph in cleaned.split("\n\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_split_long_text(paragraph, chunk_size, overlap))
            continue

        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current.strip())
            current = paragraph

    if current:
        chunks.append(current.strip())

    metadata = base_metadata or {}
    return [
        TextChunk(chunk_index=index, content=content, metadata={**metadata, "chunk_index": index})
        for index, content in enumerate(chunks)
        if content
    ]


def _split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks
