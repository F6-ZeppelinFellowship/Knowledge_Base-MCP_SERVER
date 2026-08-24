"""
Document upload, list, and delete REST endpoints.

Fix: the `label` field is optional. When omitted or blank the filename
(without extension) is used as the label, preventing the
"Ingestion failed: label empty or too long" error that occurs when no
label is sent in the multipart form data.
"""

import os
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

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
# Label resolution (THE CORE FIX)
# ---------------------------------------------------------------------------

def _resolve_label(label: Optional[str], filename: str) -> str:
    """
    Return a clean label for the document.

    Priority:
      1. The caller-supplied ``label`` (stripped, if non-empty and within limits).
      2. The filename stem (everything before the last dot) as a safe fallback.

    Raises HTTPException 422 only if the resolved label is still empty after
    all fallback attempts, which should never happen for a valid upload.
    """
    if label:
        label = label.strip()

    # Fall back to filename stem when label is missing or blank
    if not label:
        label = os.path.splitext(filename)[0].strip() if filename else ""

    # Truncate gracefully rather than rejecting — keeps UX smooth
    if len(label) > _LABEL_MAX_LEN:
        label = label[:_LABEL_MAX_LEN]

    if not label:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not determine a valid label for the document. "
                   "Please provide a non-empty label.",
        )

    return label


# ---------------------------------------------------------------------------
# POST /documents/upload
# ---------------------------------------------------------------------------

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="Document file (.pdf, .md, .txt)"),
    label: Optional[str] = Form(
        default=None,
        description=(
            "Human-readable name for the document. "
            "Defaults to the filename when omitted."
        ),
    ),
    user_id: str = Form(
        default="anonymous",
        description="Tenant / user identifier for multi-tenant isolation.",
    ),
    chunk_size: Optional[int] = Form(default=None),
    chunk_overlap: Optional[int] = Form(default=None),
    storage: QdrantStorage = Depends(get_storage),
):
    """
    Upload and ingest a document into the vector store.

    - **file**: The document to upload (PDF, Markdown, or plain text).
    - **label**: Optional display name. Falls back to the filename when not supplied.
    - **user_id**: Scopes the document to a specific tenant/user.
    """
    # ── Resolve label (THE FIX) ──────────────────────────────────────────────
    resolved_label = _resolve_label(label, file.filename or "")

    # ── Read file bytes ──────────────────────────────────────────────────────
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

    # ── Ingest ───────────────────────────────────────────────────────────────
    document_id = str(uuid.uuid4())
    try:
        result = ingest_document(
            file_content=file_bytes,
            filename=file.filename or resolved_label,
            user_id=user_id,
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
    user_id: str = "anonymous",
    storage: QdrantStorage = Depends(get_storage),
):
    """List all documents stored for a given user."""
    try:
        sources = storage.list_sources(user_id=user_id)
    except Exception as exc:
        logger.exception("Failed to list documents for user '%s'", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {exc}",
        )
    return {"user_id": user_id, "documents": sources}


# ---------------------------------------------------------------------------
# DELETE /documents/{document_id}
# ---------------------------------------------------------------------------

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: str,
    user_id: str = "anonymous",
    storage: QdrantStorage = Depends(get_storage),
):
    """Delete all vector chunks for a specific document."""
    try:
        storage.delete_document_chunks(document_id=document_id, user_id=user_id)
    except Exception as exc:
        logger.exception(
            "Failed to delete document '%s' for user '%s'", document_id, user_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {exc}",
        )
    return {"document_id": document_id, "user_id": user_id, "status": "deleted"}
