from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth, documents, search

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Personal Knowledge-Base MCP Server REST API",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(search.router, prefix="/search", tags=["search"])


@app.get("/health", tags=["health"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "version": settings.VERSION}
