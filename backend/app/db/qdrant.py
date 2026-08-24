import uuid
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
    Condition,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantStorage:
    """Qdrant storage client and schema manager for vector database operations."""

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """
        Initialize Qdrant client safely with fallback to in-memory mode.
        """
        if location:
            self.client = QdrantClient(location=location, check_compatibility=False)
        else:
            q_url = (url or settings.QDRANT_URL or "").strip()
            q_key = api_key or settings.QDRANT_API_KEY

            # If QDRANT_URL is omitted or invalid, default to in-memory vector storage
            if not q_url:
                logger.warning("No valid QDRANT_URL provided. Falling back to in-memory mode.")
                self.client = QdrantClient(location=":memory:", check_compatibility=False)
            else:
                try:
                    self.client = QdrantClient(
                        url=q_url,
                        api_key=q_key or None,
                        check_compatibility=False,
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to connect to Qdrant at {q_url}: {e}. Falling back to in-memory mode."
                    )
                    self.client = QdrantClient(location=":memory:", check_compatibility=False)

    def ensure_collection_exists(
        self,
        collection_name: Optional[str] = None,
        vector_size: Optional[int] = None,
    ) -> bool:
        """
        Ensure Qdrant collection exists with vector parameters and payload index on user_id.
        """
        col_name = collection_name or settings.QDRANT_COLLECTION_NAME
        dim = vector_size or getattr(settings, "EMBEDDING_DIMENSION", 384)

        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if col_name not in collections:
                logger.info(f"Creating collection '{col_name}' with vector dim {dim}")
                self.client.create_collection(
                    collection_name=col_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
                try:
                    self.client.create_payload_index(
                        collection_name=col_name,
                        field_name="user_id",
                        field_schema=PayloadSchemaType.KEYWORD,
                    )
                    self.client.create_payload_index(
                        collection_name=col_name,
                        field_name="document_id",
                        field_schema=PayloadSchemaType.KEYWORD,
                    )
                except Exception as index_err:
                    logger.debug(f"Payload index notice: {index_err}")
            return True
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection '{col_name}' exists: {e}")
            raise e

    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        vectors: List[List[float]],
        user_id: str,
        document_id: str,
        filename: str,
        collection_name: Optional[str] = None,
    ) -> List[str]:
        """
        Upsert chunk payload objects along with vector embeddings into Qdrant.
        """
        col_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.ensure_collection_exists(collection_name=col_name, vector_size=len(vectors[0]) if vectors else None)

        points: List[PointStruct] = []
        point_ids: List[str] = []

        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)

            payload = {
                "chunk_id": point_id,
                "document_id": document_id,
                "user_id": user_id,
                "filename": filename,
                "chunk_index": i,
                "content": chunk.get("content", ""),
                "metadata": chunk.get("metadata", {}),
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        if points:
            self.client.upsert(
                collection_name=col_name,
                points=points,
            )

        return point_ids

    def search(
        self,
        query_vector: List[float],
        user_id: Optional[str] = None,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search Qdrant for similar vectors with optional user_id payload filter and score cutoff.
        """
        col_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.ensure_collection_exists(collection_name=col_name, vector_size=len(query_vector))

        query_filter = None
        if user_id:
            must_list: List[Condition] = [
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id),
                )
            ]
            query_filter = Filter(must=must_list)

        try:
            res = self.client.query_points(
                collection_name=col_name,
                query=query_vector,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=score_threshold,
            )
            results = res.points
        except (ValueError, Exception) as e:
            logger.warning(f"Search query error: {e}")
            return []

        output = []
        for res_point in results:
            payload = res_point.payload or {}
            output.append({
                "chunk_id": res_point.id,
                "score": float(res_point.score),
                "document_id": payload.get("document_id"),
                "user_id": payload.get("user_id"),
                "filename": payload.get("filename"),
                "chunk_index": payload.get("chunk_index"),
                "content": payload.get("content"),
                "metadata": payload.get("metadata", {}),
            })

        return output

    def delete_document_chunks(
        self,
        document_id: str,
        user_id: Optional[str] = None,
        collection_name: Optional[str] = None,
    ) -> bool:
        """
        Delete all vector points belonging to a specific document_id (and user_id if provided).
        """
        col_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.ensure_collection_exists(collection_name=col_name)

        must_conditions: List[Condition] = [
            FieldCondition(key="document_id", match=MatchValue(value=document_id))
        ]
        if user_id:
            must_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )

        try:
            self.client.delete(
                collection_name=col_name,
                points_selector=rest.FilterSelector(
                    filter=Filter(must=must_conditions)
                ),
            )
        except Exception as e:
            logger.warning(f"Error deleting chunks for document {document_id}: {e}")
        return True

    def get_document_chunks(
        self,
        document_id: str,
        user_id: Optional[str] = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a given document sorted by chunk index.
        """
        col_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.ensure_collection_exists(collection_name=col_name)

        must_conditions: List[Condition] = [
            FieldCondition(key="document_id", match=MatchValue(value=document_id))
        ]
        if user_id:
            must_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )

        scroll_filter = Filter(must=must_conditions)
        try:
            records, _ = self.client.scroll(
                collection_name=col_name,
                scroll_filter=scroll_filter,
                limit=1000,
                with_payload=True,
                with_vectors=False,
            )
        except (ValueError, Exception):
            return []

        chunks = []
        for rec in records:
            payload = rec.payload or {}
            chunks.append({
                "chunk_id": rec.id,
                "document_id": payload.get("document_id"),
                "user_id": payload.get("user_id"),
                "filename": payload.get("filename"),
                "chunk_index": payload.get("chunk_index", 0),
                "content": payload.get("content"),
                "metadata": payload.get("metadata", {}),
            })

        chunks.sort(key=lambda x: x["chunk_index"])
        return chunks

    def list_sources(
        self,
        user_id: Optional[str] = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List distinct document sources/filenames available for a user.
        """
        col_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.ensure_collection_exists(collection_name=col_name)

        must_conditions: List[Condition] = []
        if user_id:
            must_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )

        scroll_filter = Filter(must=must_conditions) if must_conditions else None
        
        try:
            records, _ = self.client.scroll(
                collection_name=col_name,
                scroll_filter=scroll_filter,
                limit=2000,
                with_payload=True,
                with_vectors=False,
            )
        except (ValueError, Exception):
            return []

        docs: Dict[str, Dict[str, Any]] = {}
        for rec in records:
            payload = rec.payload or {}
            doc_id = payload.get("document_id")
            if doc_id and doc_id not in docs:
                docs[doc_id] = {
                    "document_id": doc_id,
                    "filename": payload.get("filename"),
                    "user_id": payload.get("user_id"),
                    "chunk_count": 1,
                }
            elif doc_id in docs:
                docs[doc_id]["chunk_count"] += 1

        return list(docs.values())


# Singleton instance for application use
qdrant_db = QdrantStorage(location=":memory:")