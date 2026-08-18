import pytest
from app.db.qdrant import QdrantStorage
from app.services.embeddings import EmbeddingService
from app.services.ingestion import ingest_document
from app.services.retrieval import search_qdrant, get_document, list_sources, delete_document


@pytest.fixture
def test_setup():
    storage = QdrantStorage(location=":memory:")
    storage.ensure_collection_exists(collection_name="documents", vector_size=384)
    embedder = EmbeddingService(model_name="all-MiniLM-L6-v2")
    return storage, embedder


def test_ingest_and_search_qdrant(test_setup):
    storage, embedder = test_setup

    doc_content = """
    # Quantum Computing Overview
    Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics to solve problems too complex for classical computers.
    Superposition and entanglement are key quantum phenomena utilized by qubits.
    """

    ingest_res = ingest_document(
        file_content=doc_content,
        filename="quantum_notes.md",
        user_id="alice",
        document_id="doc_quantum_101",
        storage=storage,
        embedder=embedder,
    )

    assert ingest_res["status"] == "success"
    assert ingest_res["chunk_count"] > 0
    assert ingest_res["document_id"] == "doc_quantum_101"

    # Search with relevant query
    search_results = search_qdrant(
        query="What is quantum mechanics in computing?",
        user_id="alice",
        top_k=3,
        storage=storage,
        embedder=embedder,
    )

    assert len(search_results) > 0
    assert search_results[0]["document_id"] == "doc_quantum_101"
    assert search_results[0]["score"] > 0.4


def test_search_score_threshold_filtering(test_setup):
    storage, embedder = test_setup

    doc_content = "Python is an interpreted high-level general-purpose programming language."
    ingest_document(
        file_content=doc_content,
        filename="python.txt",
        user_id="bob",
        document_id="doc_py",
        storage=storage,
        embedder=embedder,
    )

    # Completely irrelevant query with high score threshold should return empty results
    results_high_cutoff = search_qdrant(
        query="Astronomy and space exploration telescopes on Mars",
        user_id="bob",
        top_k=3,
        score_threshold=0.85,
        storage=storage,
        embedder=embedder,
    )

    assert len(results_high_cutoff) == 0


def test_get_document_and_list_sources(test_setup):
    storage, embedder = test_setup

    ingest_document(
        file_content="First chunk of note.\n\nSecond chunk of note.",
        filename="my_note.md",
        user_id="carol",
        document_id="doc_note_1",
        chunk_size=30,
        chunk_overlap=5,
        storage=storage,
        embedder=embedder,
    )

    # Test list_sources
    sources = list_sources(user_id="carol", storage=storage)
    assert len(sources) == 1
    assert sources[0]["filename"] == "my_note.md"
    assert sources[0]["document_id"] == "doc_note_1"

    # Test get_document
    chunks = get_document(document_id="doc_note_1", user_id="carol", storage=storage)
    assert len(chunks) > 0
    assert chunks[0]["chunk_index"] == 0

    # Test delete_document
    delete_document(document_id="doc_note_1", user_id="carol", storage=storage)
    sources_after_del = list_sources(user_id="carol", storage=storage)
    assert len(sources_after_del) == 0
