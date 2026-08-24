from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.api.auth import get_current_user
from app.services.retrieval import search_qdrant
from app.services.llm_service import generate_rag_answer

router = APIRouter(prefix="/search", tags=["Search"])

class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@router.get("", response_model=RAGResponse)
@router.get("/", response_model=RAGResponse, include_in_schema=False)
async def search_notes(
    q: str = Query(..., description="Search query string"),
    top_k: int = Query(5, ge=1, le=20),
    score_threshold: Optional[float] = Query(0.0, ge=0.0, le=1.0),
    current_user: str = Depends(get_current_user)
):
    # 1. Fetch vector matches via retrieval service (handles text-to-embedding conversion)
    search_results = search_qdrant(
        query=q,
        user_id=current_user,
        top_k=top_k,
        score_threshold=score_threshold
    )

    # 2. Pass query and retrieved vector context into LLM generator
    answer = generate_rag_answer(q, search_results)

    # 3. Return response payload matching RAGResponse schema
    return {
        "answer": answer,
        "sources": search_results
    }