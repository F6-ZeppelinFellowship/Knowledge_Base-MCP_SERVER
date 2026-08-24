"""
FastMCP server for the Personal Knowledge Base.

Run:

    python -m app.mcp_server.server
"""

from fastmcp import FastMCP

from app.mcp_server.tools import (
    search_notes,
    get_document,
    list_sources,
)


mcp = FastMCP("personal-kb")


mcp.tool()(search_notes)
mcp.tool()(get_document)
mcp.tool()(list_sources)


if __name__ == "__main__":
    mcp.run()
