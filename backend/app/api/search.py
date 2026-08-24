from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.api.auth import get_current_user
from app.services.retrieval import search_qdrant

router = APIRouter(prefix="/search", tags=["Search"])


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    score_threshold: Optional[float] = 0.70

@router.post("/", response_model=List[Dict[str, Any]])
async def search_notes(
    body: SearchQuery,
    current_user: str = Depends(get_current_user)
):
    """Execute vector search scoped to the authenticated user."""
    results = search_qdrant(
        query=body.query,
        user_id=current_user,
        top_k=body.top_k,
        score_threshold=body.score_threshold
    )
    return results