"""
MCP tool implementations for the Personal Knowledge Base.

Engineer 2 owns this module.

The MCP layer depends on the public retrieval functions from
app.services.retrieval rather than directly accessing Qdrant.
"""

import os
from typing import Any, Dict, List, Optional

from app.services.retrieval import (
    search_qdrant,
    get_document as retrieve_document,
    list_sources as retrieve_sources,
)


# Project requirement from README:
# cosine similarity >= 0.72
DEFAULT_SCORE_THRESHOLD = float(
    os.getenv("MCP_SCORE_THRESHOLD", "0.72")
)


def _resolve_user_id(user_id: Optional[str]) -> str:
    """
    Resolve the tenant/user ID.

    The ID can either be supplied directly by the MCP client or configured
    through MCP_USER_ID for a dedicated MCP server instance.
    """

    resolved_user_id = user_id or os.getenv("MCP_USER_ID")

    if not resolved_user_id:
        raise ValueError(
            "user_id is required. "
            "Pass user_id explicitly or configure MCP_USER_ID."
        )

    return resolved_user_id


def search_notes(
    query: str,
    user_id: Optional[str] = None,
    top_k: int = 5,
    score_threshold: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Perform semantic search over the user's personal knowledge base.

    Results below the relevance threshold are rejected.
    """

    if not query or not query.strip():
        return []

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    threshold = (
        DEFAULT_SCORE_THRESHOLD
        if score_threshold is None
        else score_threshold
    )

    tenant_id = _resolve_user_id(user_id)

    return search_qdrant(
        query=query,
        user_id=tenant_id,
        top_k=top_k,
        score_threshold=threshold,
    )


def get_document(
    document_id: str,
    user_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve all chunks belonging to a document.

    Tenant isolation is enforced by passing user_id to the retrieval layer.
    """

    if not document_id or not document_id.strip():
        raise ValueError("document_id must not be empty")

    tenant_id = _resolve_user_id(user_id)

    return retrieve_document(
        document_id=document_id,
        user_id=tenant_id,
    )


def list_sources(
    user_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List documents available to the current tenant.
    """

    tenant_id = _resolve_user_id(user_id)

    return retrieve_sources(
        user_id=tenant_id
    )
