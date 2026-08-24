import pytest
from app.services.ingestion import (
    parse_markdown,
    parse_text,
    parse_document,
    chunk_text,
    _fallback_split_text,
)


def test_parse_markdown():
    content = "# Title\n\nThis is a **markdown** document."
    parsed = parse_markdown(content)
    assert "# Title" in parsed
    assert "markdown" in parsed

    bytes_content = content.encode("utf-8")
    parsed_bytes = parse_markdown(bytes_content)
    assert parsed_bytes == parsed


def test_parse_text():
    content = "Simple plain text document content."
    parsed = parse_text(content)
    assert parsed == content

    bytes_content = content.encode("latin-1")
    parsed_bytes = parse_text(bytes_content)
    assert parsed_bytes == content


def test_parse_document_extension_routing():
    md_content = "# Header\nBody"
    assert parse_document(md_content, "notes.md") == md_content

    txt_content = "Plain text"
    assert parse_document(txt_content, "file.txt") == txt_content


def test_chunk_text_size_and_overlap():
    sample_text = (
        "Vector databases empower modern AI applications with high-speed similarity search over dense embeddings. "
        "Dynamic chunking ensures that document passages are divided into semantically coherent segments with "
        "configurable token or character overlaps. This prevents boundary truncation and improves retrieval quality."
    )

    chunk_size = 100
    chunk_overlap = 20
    chunks = chunk_text(sample_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    assert len(chunks) > 0
    for i, c in enumerate(chunks):
        assert "content" in c
        assert "metadata" in c
        assert c["metadata"]["chunk_index"] == i
        assert len(c["content"]) <= chunk_size + 50  # Allow buffer for word boundary splits


def test_fallback_split_text():
    sample_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chunks = _fallback_split_text(sample_text, chunk_size=10, chunk_overlap=2)
    assert len(chunks) == 3
    assert chunks[0] == "ABCDEFGHIJ"
    assert chunks[1] == "IJKLMNOPQR"
    assert chunks[2] == "QRSTUVWXYZ"
