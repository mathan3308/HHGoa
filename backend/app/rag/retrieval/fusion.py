from typing import List, Dict, Any, Optional

def reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    rrf_k: int = 60,
    final_top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Combines dense semantic search and sparse BM25 search results using Reciprocal Rank Fusion (RRF).
    Formula: score(d) = sum(1 / (k + rank(d)))
    Scores are normalized to [0.0, 1.0] relative to max rank 1 RRF score.
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    # Accumulate dense ranks
    for rank, item in enumerate(dense_results, start=1):
        chunk_id = item.get("chunk_id", f"dense_{rank}")
        scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (rrf_k + rank))
        if chunk_id not in doc_map:
            doc_map[chunk_id] = item

    # Accumulate sparse ranks
    for rank, item in enumerate(sparse_results, start=1):
        chunk_id = item.get("chunk_id", f"sparse_{rank}")
        scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (rrf_k + rank))
        if chunk_id not in doc_map:
            doc_map[chunk_id] = item

    # Sort candidates by combined RRF score descending
    sorted_chunks = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:final_top_k]

    # Calculate theoretical max RRF score for normalization
    has_both = bool(dense_results and sparse_results)
    max_possible_rrf = (2.0 / (rrf_k + 1.0)) if has_both else (1.0 / (rrf_k + 1.0))

    fused_results = []
    for chunk_id, rrf_score in sorted_chunks:
        doc = dict(doc_map[chunk_id])
        normalized_score = min(1.0, rrf_score / max_possible_rrf) if max_possible_rrf > 0 else rrf_score
        doc["relevance_score"] = float(round(normalized_score, 4))
        fused_results.append(doc)

    return fused_results
