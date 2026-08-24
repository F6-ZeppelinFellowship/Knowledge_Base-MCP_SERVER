import pytest
from app.db.qdrant import QdrantStorage


@pytest.fixture
def memory_qdrant():
    """Create in-memory Qdrant instance for isolated testing."""
    storage = QdrantStorage(location=":memory:")
    storage.ensure_collection_exists(collection_name="test_collection", vector_size=384)
    return storage


def test_qdrant_upsert_and_search(memory_qdrant):
    chunks = [
        {"content": "Artificial intelligence and machine learning notes.", "metadata": {}},
        {"content": "Database design and SQL optimization guide.", "metadata": {}},
    ]
    # Synthetic vectors
    vec1 = [0.1] * 384
    vec2 = [0.9] * 384

    point_ids = memory_qdrant.upsert_chunks(
        chunks=chunks,
        vectors=[vec1, vec2],
        user_id="user_123",
        document_id="doc_001",
        filename="ai_notes.txt",
        collection_name="test_collection",
    )

    assert len(point_ids) == 2

    # Query matching vec1 closely
    query_vec = [0.1] * 384
    results = memory_qdrant.search(
        query_vector=query_vec,
        user_id="user_123",
        top_k=2,
        collection_name="test_collection",
    )

    assert len(results) == 2
    assert results[0]["user_id"] == "user_123"
    assert results[0]["document_id"] == "doc_001"
    assert results[0]["filename"] == "ai_notes.txt"


def test_qdrant_multi_tenant_isolation(memory_qdrant):
    chunks = [{"content": "Secret note for user A", "metadata": {}}]
    vec = [0.5] * 384

    memory_qdrant.upsert_chunks(
        chunks=chunks,
        vectors=[vec],
        user_id="user_A",
        document_id="doc_A",
        filename="user_a.txt",
        collection_name="test_collection",
    )

    # Search as user_B should return 0 results
    results_user_B = memory_qdrant.search(
        query_vector=vec,
        user_id="user_B",
        top_k=5,
        collection_name="test_collection",
    )
    assert len(results_user_B) == 0

    # Search as user_A should return the chunk
    results_user_A = memory_qdrant.search(
        query_vector=vec,
        user_id="user_A",
        top_k=5,
        collection_name="test_collection",
    )
    assert len(results_user_A) == 1
    assert results_user_A[0]["user_id"] == "user_A"


def test_qdrant_delete_document(memory_qdrant):
    chunks = [{"content": "Temporary content to delete", "metadata": {}}]
    vec = [0.2] * 384

    memory_qdrant.upsert_chunks(
        chunks=chunks,
        vectors=[vec],
        user_id="user_del",
        document_id="doc_to_delete",
        filename="temp.txt",
        collection_name="test_collection",
    )

    memory_qdrant.delete_document_chunks(
        document_id="doc_to_delete",
        user_id="user_del",
        collection_name="test_collection",
    )

    results = memory_qdrant.search(
        query_vector=vec,
        user_id="user_del",
        top_k=5,
        collection_name="test_collection",
    )
    assert len(results) == 0
