import logging
from typing import List, Dict, Any, Optional

from app.db.qdrant import qdrant_db, QdrantStorage
from app.services.embeddings import embedding_service, EmbeddingService

logger = logging.getLogger(__name__)


def search_qdrant(
    query: str,
    user_id: Optional[str] = None,
    top_k: int = 5,
    score_threshold: Optional[float] = None,
    storage: Optional[QdrantStorage] = None,
    embedder: Optional[EmbeddingService] = None,
) -> List[Dict[str, Any]]:
    """
    Core similarity search engine over vector store.
    Formats payload to align with frontend ResultCard component expectations.
    """
    if not query or not query.strip():
        return []

    db = storage or qdrant_db
    emb_service = embedder or embedding_service

    # 1. Embed query
    query_vector = emb_service.embed_text(query)

    # 2. Search Qdrant DB
    raw_results = db.search(
        query_vector=query_vector,
        user_id=user_id,
        top_k=top_k,
        score_threshold=score_threshold,
    )

    # 3. Standardize structure for ResultCard.jsx
    formatted_results = []
    for item in raw_results:
        # Handle dict or Qdrant ScoredPoint structures
        payload = item.get("payload", item) if isinstance(item, dict) else getattr(item, "payload", {})
        score = item.get("score", 0.0) if isinstance(item, dict) else getattr(item, "score", 0.0)

        formatted_results.append({
            "chunk_text": payload.get("chunk_text") or payload.get("text") or "",
            "score": float(score),
            "source": {
                "filename": payload.get("filename") or payload.get("source_file") or "Unknown Document",
                "page": payload.get("page") or payload.get("page_number"),
            }
        })

    return formatted_results


def get_document(
    document_id: str,
    user_id: Optional[str] = None,
    storage: Optional[QdrantStorage] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve full document content by reconstructing chunks in sequence.
    """
    db = storage or qdrant_db
    return db.get_document_chunks(document_id=document_id, user_id=user_id)


def list_sources(
    user_id: Optional[str] = None,
    storage: Optional[QdrantStorage] = None,
) -> List[Dict[str, Any]]:
    """
    List available document sources/files formatted for Sidebar.jsx.
    """
    db = storage or qdrant_db
    raw_sources = db.list_sources(user_id=user_id)

    formatted_sources = []
    for src in raw_sources:
        doc_id = src.get("id") or src.get("document_id") or src.get("file_id")
        filename = src.get("filename") or src.get("source_file") or "Untitled Document"
        size_bytes = src.get("size_bytes") or src.get("file_size") or 0
        status = src.get("status", "completed")

        formatted_sources.append({
            "id": str(doc_id),
            "filename": str(filename),
            "size_bytes": int(size_bytes),
            "status": str(status)
        })

    return formatted_sources


def delete_document(
    document_id: str,
    user_id: Optional[str] = None,
    storage: Optional[QdrantStorage] = None,
) -> bool:
    """
    Delete a document and all its chunks from Qdrant vector store.
    """
    db = storage or qdrant_db
    return db.delete_document_chunks(document_id=document_id, user_id=user_id)