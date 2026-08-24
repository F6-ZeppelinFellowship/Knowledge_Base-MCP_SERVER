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

    Parameters:
    - query: Natural language search query string.
    - user_id: Optional tenant isolation user ID filter.
    - top_k: Maximum number of search results to return.
    - score_threshold: Minimum similarity score cutoff threshold (e.g., Cosine >= 0.72).
    - storage: Custom QdrantStorage instance (optional).
    - embedder: Custom EmbeddingService instance (optional).

    Returns list of dicts containing chunk metadata, content, and similarity score.
    """
    if not query or not query.strip():
        return []

    db = storage or qdrant_db
    emb_service = embedder or embedding_service

    # 1. Embed query
    query_vector = emb_service.embed_text(query)

    # 2. Search Qdrant DB with user_id payload filter and score cutoff
    results = db.search(
        query_vector=query_vector,
        user_id=user_id,
        top_k=top_k,
        score_threshold=score_threshold,
    )

    return results


def get_document(
    document_id: str,
    user_id: Optional[str] = None,
    storage: Optional[QdrantStorage] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve full document content by reconstructing chunks in sequence.

    Contract helper function for Engineer 2 (MCP) and Engineer 3 (FastAPI).
    """
    db = storage or qdrant_db
    return db.get_document_chunks(document_id=document_id, user_id=user_id)


def list_sources(
    user_id: Optional[str] = None,
    storage: Optional[QdrantStorage] = None,
) -> List[Dict[str, Any]]:
    """
    List available document sources/files for a given user.

    Contract helper function for Engineer 2 (MCP) and Engineer 3 (FastAPI).
    """
    db = storage or qdrant_db
    return db.list_sources(user_id=user_id)


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
