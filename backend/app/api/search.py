from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any, Optional
from app.api.auth import get_current_user
from app.services.retrieval import search_qdrant

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]], include_in_schema=False)
async def search_notes(
    q: str = Query(..., description="Search query string"),
    top_k: int = Query(5, ge=1, le=20),
    score_threshold: Optional[float] = Query(0.0, ge=0.0, le=1.0), # Set default to 0.0 to inspect raw scores
    current_user: str = Depends(get_current_user)
):
    results = search_qdrant(
        query=q,
        user_id=current_user,
        top_k=top_k,
        score_threshold=score_threshold
    )
    return results