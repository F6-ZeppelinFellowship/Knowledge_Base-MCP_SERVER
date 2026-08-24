import pytest
from app.services.embeddings import EmbeddingService


def test_embedding_service_dimensions():
    embedder = EmbeddingService(model_name="all-MiniLM-L6-v2")
    vector = embedder.embed_text("Vector similarity search test query")

    assert isinstance(vector, list)
    assert len(vector) == 384
    assert embedder.get_dimension() == 384


def test_embedding_service_batch_processing():
    embedder = EmbeddingService(model_name="all-MiniLM-L6-v2")
    texts = [
        "First test sentence for vector embedding.",
        "Second test sentence for retrieval validation.",
        "Third document chunk.",
    ]
    vectors = embedder.embed_documents(texts)

    assert isinstance(vectors, list)
    assert len(vectors) == 3
    for vec in vectors:
        assert isinstance(vec, list)
        assert len(vec) == 384


def test_empty_text_embedding():
    embedder = EmbeddingService(model_name="all-MiniLM-L6-v2")
    empty_vec = embedder.embed_text("")
    assert len(empty_vec) == 384
    assert all(val == 0.0 for val in empty_vec)
