"""
Retrieval evaluation for the Personal Knowledge Base.

Metrics:
    - Precision@K
    - Mean Reciprocal Rank (MRR)

The evaluation dataset contains hand-labeled query/document relationships.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.retrieval import search_qdrant


DEFAULT_TOP_K = 3
DEFAULT_SCORE_THRESHOLD = 0.72


def precision_at_k(
    retrieved_documents: List[str],
    relevant_documents: List[str],
    k: int = 3,
) -> float:
    """
    Calculate Precision@K.

    Precision@K =
        relevant documents in top K / K
    """

    if k <= 0:
        raise ValueError("k must be greater than 0")

    retrieved = retrieved_documents[:k]

    if not retrieved:
        return 0.0

    relevant = set(relevant_documents)

    relevant_count = sum(
        1 for document_id in retrieved
        if document_id in relevant
    )

    return relevant_count / len(retrieved)


def reciprocal_rank(
    retrieved_documents: List[str],
    relevant_documents: List[str],
) -> float:
    """
    Calculate reciprocal rank for one query.

    Returns 1/rank of the first relevant result.
    Returns 0 when no relevant result is found.
    """

    relevant = set(relevant_documents)

    for rank, document_id in enumerate(retrieved_documents, start=1):
        if document_id in relevant:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(
    reciprocal_ranks: List[float],
) -> float:
    """
    Calculate Mean Reciprocal Rank.
    """

    if not reciprocal_ranks:
        return 0.0

    return sum(reciprocal_ranks) / len(reciprocal_ranks)


def evaluate_query(
    query_data: Dict[str, Any],
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
) -> Dict[str, Any]:
    """
    Evaluate one query against the real retrieval engine.
    """

    query = query_data["query"]
    user_id = query_data["user_id"]
    relevant_documents = query_data["relevant_documents"]

    results = search_qdrant(
        query=query,
        user_id=user_id,
        top_k=top_k,
        score_threshold=score_threshold,
    )

    retrieved_documents = [
        result["document_id"]
        for result in results
        if result.get("document_id")
    ]

    precision = precision_at_k(
        retrieved_documents,
        relevant_documents,
        k=top_k,
    )

    rr = reciprocal_rank(
        retrieved_documents,
        relevant_documents,
    )

    return {
        "query": query,
        "retrieved_documents": retrieved_documents,
        "relevant_documents": relevant_documents,
        "precision_at_k": precision,
        "reciprocal_rank": rr,
    }


def evaluate_dataset(
    dataset_path: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
) -> Dict[str, Any]:
    """
    Evaluate all hand-labeled queries.
    """

    path = Path(dataset_path)

    with path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    results = []

    for query_data in dataset:
        result = evaluate_query(
            query_data=query_data,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        results.append(result)

    precisions = [
        result["precision_at_k"]
        for result in results
    ]

    reciprocal_ranks = [
        result["reciprocal_rank"]
        for result in results
    ]

    return {
        "num_queries": len(results),
        f"precision_at_{top_k}": (
            sum(precisions) / len(precisions)
            if precisions
            else 0.0
        ),
        "mrr": mean_reciprocal_rank(reciprocal_ranks),
        "score_threshold": score_threshold,
        "results": results,
    }


if __name__ == "__main__":
    dataset = Path(__file__).parent / "test_queries.json"

    evaluation = evaluate_dataset(
        dataset_path=str(dataset),
        top_k=DEFAULT_TOP_K,
        score_threshold=DEFAULT_SCORE_THRESHOLD,
    )

    print("=" * 60)
    print("PERSONAL KNOWLEDGE BASE RETRIEVAL EVALUATION")
    print("=" * 60)

    print(f"Queries: {evaluation['num_queries']}")
    print(
        f"Precision@{DEFAULT_TOP_K}: "
        f"{evaluation[f'precision_at_{DEFAULT_TOP_K}']:.4f}"
    )
    print(f"MRR: {evaluation['mrr']:.4f}")
    print(f"Threshold: {evaluation['score_threshold']}")
