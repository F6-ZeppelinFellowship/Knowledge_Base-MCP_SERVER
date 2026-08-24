"""
Document upload, list, and delete REST endpoints.

Fix: optional label fallback, multi-tenant isolation with authenticated user dependency.
"""

import os
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.auth import get_current_user
from app.services.ingestion import ingest_document
from app.db.qdrant import qdrant_db, QdrantStorage

logger = logging.getLogger(__name__)

router = APIRouter()

# Maximum characters allowed for a document label
_LABEL_MAX_LEN = 255


# ---------------------------------------------------------------------------
# Dependency: injectable Qdrant storage (can be overridden in tests)
# ---------------------------------------------------------------------------

def get_storage() -> QdrantStorage:
    """Return the application-level Qdrant storage singleton."""
    return qdrant_db


# ---------------------------------------------------------------------------
# Label resolution
# ---------------------------------------------------------------------------

def _resolve_label(label: Optional[str], filename: str) -> str:
    """
    Return a clean label for the document.
    Priority:
      1. Caller-supplied label (stripped).
      2. Filename stem fallback.
    """
    if label:
        label = label.strip()

    if not label:
        label = os.path.splitext(filename)[0].strip() if filename else ""

    if len(label) > _LABEL_MAX_LEN:
        label = label[:_LABEL_MAX_LEN]

    if not label:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not determine a valid label for the document.",
        )

    return label


# ---------------------------------------------------------------------------
# POST /documents/upload
# ---------------------------------------------------------------------------

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="Document file (.pdf, .md, .txt)"),
    label: Optional[str] = Form(default=None),
    chunk_size: Optional[int] = Form(default=None),
    chunk_overlap: Optional[int] = Form(default=None),
    current_user: str = Depends(get_current_user),
    storage: QdrantStorage = Depends(get_storage),
):
    """
    Upload and ingest a document scoped to the current authenticated user.
    """
    resolved_label = _resolve_label(label, file.filename or "")

    try:
        file_bytes = await file.read()
    except Exception as exc:
        logger.error("Failed to read uploaded file: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {exc}",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )

    document_id = str(uuid.uuid4())
    try:
        result = ingest_document(
            file_content=file_bytes,
            filename=file.filename or resolved_label,
            user_id=current_user,
            document_id=document_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            storage=storage,
        )
    except ValueError as exc:
        logger.warning("Ingestion validation error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ingestion failed: {exc}",
        )
    except Exception as exc:
        logger.exception("Unexpected ingestion error for document '%s'", resolved_label)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {exc}",
        )

    return {
        "document_id": result["document_id"],
        "label": resolved_label,
        "filename": result["filename"],
        "user_id": result["user_id"],
        "chunk_count": result["chunk_count"],
        "status": "uploaded",
    }


# ---------------------------------------------------------------------------
# GET /documents/list
# ---------------------------------------------------------------------------

@router.get("/list")
def list_documents(
    current_user: str = Depends(get_current_user),
    storage: QdrantStorage = Depends(get_storage),
):
    """List all documents stored for the current user."""
    try:
        sources = storage.list_sources(user_id=current_user)
    except Exception as exc:
        logger.exception("Failed to list documents for user '%s'", current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {exc}",
        )
    return {"user_id": current_user, "documents": sources}


# ---------------------------------------------------------------------------
# DELETE /documents/{document_id}
# ---------------------------------------------------------------------------

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: str,
    current_user: str = Depends(get_current_user),
    storage: QdrantStorage = Depends(get_storage),
):
    """Delete all vector chunks for a specific document."""
    try:
        storage.delete_document_chunks(document_id=document_id, user_id=current_user)
    except Exception as exc:
        logger.exception(
            "Failed to delete document '%s' for user '%s'", document_id, current_user
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {exc}",
        )
    return {"document_id": document_id, "user_id": current_user, "status": "deleted"}