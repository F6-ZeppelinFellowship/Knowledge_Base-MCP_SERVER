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
        Initialize Qdrant client. If location=":memory:" or url is provided, connects accordingly.
        Falls back to in-memory client if connection fails.
        """
        if location:
            self.client = QdrantClient(location=location)
        else:
            q_url = url or settings.QDRANT_URL
            q_key = api_key or settings.QDRANT_API_KEY
            try:
                self.client = QdrantClient(url=q_url, api_key=q_key or None)
            except Exception as e:
                logger.warning(f"Failed to connect to Qdrant at {q_url}: {e}. Falling back to in-memory mode.")
                self.client = QdrantClient(location=":memory:")

    def ensure_collection_exists(
        self,
        collection_name: Optional[str] = None,
        vector_size: Optional[int] = None,
    ) -> bool:
        """
        Ensure Qdrant collection exists with vector parameters and payload index on user_id.
        """
        col_name = collection_name or settings.QDRANT_COLLECTION_NAME
        dim = vector_size or settings.EMBEDDING_DIMENSION

        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if col_name not in collections:
                logger.info(f"Creating collection '{col_name}' with vector dim {dim}")
                self.client.create_collection(
                    collection_name=col_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
                # Create payload indexes for fast multi-tenant filtering (best effort for remote/server Qdrant)
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
                    logger.debug(f"Payload index notice (ignored for in-memory Qdrant): {index_err}")
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
        Returns a list of point IDs created.
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
        Search Qdrant for similar vectors with optional user_id multi-tenant payload filter and score cutoff.
        """
        col_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.ensure_collection_exists(collection_name=col_name, vector_size=len(query_vector))

        query_filter = None
        if user_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id),
                    )
                ]
            )

        if hasattr(self.client, "query_points"):
            res = self.client.query_points(
                collection_name=col_name,
                query=query_vector,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=score_threshold,
            )
            results = res.points
        else:
            results = self.client.search(
                collection_name=col_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=score_threshold,
            )

        output = []
        for res_point in results:
            output.append({
                "chunk_id": res_point.id,
                "score": float(res_point.score),
                "document_id": res_point.payload.get("document_id"),
                "user_id": res_point.payload.get("user_id"),
                "filename": res_point.payload.get("filename"),
                "chunk_index": res_point.payload.get("chunk_index"),
                "content": res_point.payload.get("content"),
                "metadata": res_point.payload.get("metadata", {}),
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
        must_conditions = [
            FieldCondition(key="document_id", match=MatchValue(value=document_id))
        ]
        if user_id:
            must_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )

        self.client.delete(
            collection_name=col_name,
            points_selector=rest.FilterSelector(
                filter=Filter(must=must_conditions)
            ),
        )
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
        must_conditions = [
            FieldCondition(key="document_id", match=MatchValue(value=document_id))
        ]
        if user_id:
            must_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )

        scroll_filter = Filter(must=must_conditions)
        records, _ = self.client.scroll(
            collection_name=col_name,
            scroll_filter=scroll_filter,
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )

        chunks = []
        for rec in records:
            chunks.append({
                "chunk_id": rec.id,
                "document_id": rec.payload.get("document_id"),
                "user_id": rec.payload.get("user_id"),
                "filename": rec.payload.get("filename"),
                "chunk_index": rec.payload.get("chunk_index", 0),
                "content": rec.payload.get("content"),
                "metadata": rec.payload.get("metadata", {}),
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
        must_conditions = []
        if user_id:
            must_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )

        scroll_filter = Filter(must=must_conditions) if must_conditions else None
        records, _ = self.client.scroll(
            collection_name=col_name,
            scroll_filter=scroll_filter,
            limit=2000,
            with_payload=True,
            with_vectors=False,
        )

        docs: Dict[str, Dict[str, Any]] = {}
        for rec in records:
            doc_id = rec.payload.get("document_id")
            if doc_id and doc_id not in docs:
                docs[doc_id] = {
                    "document_id": doc_id,
                    "filename": rec.payload.get("filename"),
                    "user_id": rec.payload.get("user_id"),
                    "chunk_count": 1,
                }
            elif doc_id in docs:
                docs[doc_id]["chunk_count"] += 1

        return list(docs.values())


# Singleton instance for application use
qdrant_db = QdrantStorage()
