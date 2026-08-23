"""
FastMCP server for the Personal Knowledge Base.

Run from the backend directory with:

    python -m app.mcp_server.server
"""

from fastmcp import FastMCP

from app.mcp_server.tools import (
    search_notes,
    get_document,
    list_sources,
)


mcp = FastMCP(
    "personal-kb"
)


@mcp.tool()
def search_notes_tool(
    query: str,
    user_id: str,
    top_k: int = 5,
    score_threshold: float = 0.72,
):
    """
    Search the user's personal knowledge base using semantic similarity.

    Args:
        query: Natural language question or search query.
        user_id: Tenant/user identifier.
        top_k: Maximum number of results.
        score_threshold: Minimum cosine similarity score.
    """
    return search_notes(
        query=query,
        user_id=user_id,
        top_k=top_k,
        score_threshold=score_threshold,
    )


@mcp.tool()
def get_document_tool(
    document_id: str,
    user_id: str,
):
    """
    Retrieve all chunks belonging to a document.
    """
    return get_document(
        document_id=document_id,
        user_id=user_id,
    )


@mcp.tool()
def list_sources_tool(
    user_id: str,
):
    """
    List all document sources available to the user.
    """
    return list_sources(
        user_id=user_id,
    )


if __name__ == "__main__":
    mcp.run()
