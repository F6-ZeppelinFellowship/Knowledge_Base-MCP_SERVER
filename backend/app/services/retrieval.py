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
    Formats payload to support both API consumers and UI components.
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

    # 3. Standardize structure for ResultCard.jsx while preserving raw core keys
    formatted_results = []
    for item in raw_results:
        payload = item.get("payload", item) if isinstance(item, dict) else getattr(item, "payload", {})
        score = item.get("score", 0.0) if isinstance(item, dict) else getattr(item, "score", 0.0)
        metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}

        content = (
            payload.get("content")
            or payload.get("chunk_text")
            or payload.get("text")
            or ""
        )
        filename = (
            payload.get("filename")
            or payload.get("source_file")
            or metadata.get("filename")
            or "Unknown Document"
        )
        page = payload.get("page") or payload.get("page_number") or metadata.get("page")

        formatted_results.append({
            "chunk_id": payload.get("chunk_id", item.get("chunk_id") if isinstance(item, dict) else None),
            "document_id": payload.get("document_id", item.get("document_id") if isinstance(item, dict) else None),
            "content": content,
            "chunk_text": content,
            "score": float(score),
            "filename": filename,
            "source": {
                "filename": filename,
                "page": page,
            },
            "metadata": metadata,
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
    List available document sources/files formatted for API contracts and Sidebar.jsx.
    """
    db = storage or qdrant_db
    raw_sources = db.list_sources(user_id=user_id)

    formatted_sources = []
    for src in raw_sources:
        doc_id = src.get("document_id") or src.get("id") or src.get("file_id") or ""
        filename = src.get("filename") or src.get("source_file") or "Untitled Document"
        size_bytes = src.get("size_bytes") or src.get("file_size") or 0
        status = src.get("status", "completed")
        chunk_count = src.get("chunk_count", 0)

        formatted_sources.append({
            "id": str(doc_id),
            "document_id": str(doc_id),
            "filename": str(filename),
            "size_bytes": int(size_bytes),
            "status": str(status),
            "chunk_count": int(chunk_count),
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