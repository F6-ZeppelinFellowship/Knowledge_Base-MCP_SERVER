import logging
from app.db.qdrant import qdrant_db
from app.services.embeddings import embedding_service
from app.services.retrieval import search_qdrant, list_sources, get_document, delete_document

logging.basicConfig(level=logging.INFO)

def test_rag_pipeline():
    # 1. Embedding Service
    vector = embedding_service.embed_text("Test security vector pipeline")
    assert len(vector) > 0

    # 2. Qdrant Upsert
    test_user = "user_test_123"
    test_doc = "doc_test_456"
    chunks = [
        {"content": "CyberGuard LLM fine-tunes Llama models using QLoRA for instruction tasks.", "metadata": {"page": 1}},
        {"content": "InjecGuard utilizes DPO for security alignment against injection vectors.", "metadata": {"page": 2}},
    ]
    vectors = embedding_service.embed_documents([c["content"] for c in chunks])
    
    point_ids = qdrant_db.upsert_chunks(
        chunks=chunks,
        vectors=vectors,
        user_id=test_user,
        document_id=test_doc,
        filename="security_overview.pdf",
    )
    assert len(point_ids) == 2

    # 3. Similarity Search
    results = search_qdrant(query="What is InjecGuard using?", user_id=test_user, top_k=2)
    assert len(results) > 0
    assert "InjecGuard" in results[0]["content"]

    # 4. Document Retrieval & Sources
    sources = list_sources(user_id=test_user)
    assert len(sources) > 0

    doc_chunks = get_document(document_id=test_doc, user_id=test_user)
    assert len(doc_chunks) == 2

    # 5. Document Deletion
    deleted = delete_document(document_id=test_doc, user_id=test_user)
    assert deleted is True

    after_sources = list_sources(user_id=test_user)
    assert len(after_sources) == 0