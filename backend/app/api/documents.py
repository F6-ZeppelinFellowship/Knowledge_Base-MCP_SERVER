import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.api.auth import get_current_user
from app.services.ingestion import ingest_document
from app.services.retrieval import list_sources, delete_document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Save uploaded file, run Member 1's ingestion pipeline, and store in Qdrant."""
    filename = file.filename or "uploaded_document.pdf"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".md", ".txt"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    try:
        content = await file.read()
        res = ingest_document(
            file_content=content,
            filename=filename,
            user_id=current_user
        )
        return {
            "message": "File processed and indexed successfully",
            "document_id": res["document_id"],
            "filename": filename,
            "chunks_created": res["chunk_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/list", response_model=List[Dict[str, Any]])
async def list_user_documents(current_user: str = Depends(get_current_user)):
    """Fetch indexed document sources for the authenticated user."""
    return list_sources(user_id=current_user)


@router.delete("/{document_id}")
async def remove_document(
    document_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete document and vector chunks from Qdrant."""
    success = delete_document(document_id=document_id, user_id=current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found or delete failed")
    return {"message": f"Document {document_id} successfully deleted"}