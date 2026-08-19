from typing import List, Dict, Any, Tuple

class RelevanceGuard:
    """
    Tier 2: Off-topic / Retrieval Relevance Score Guard.
    Validates retrieved candidate context quality against configured threshold.
    """
    def __init__(self, threshold: float = 0.10):
        self.threshold = threshold

    def validate(self, candidates: List[Dict[str, Any]]) -> Tuple[bool, str]:
        if not candidates:
            return False, "insufficient_retrieval_context"

        top_score = max([c.get("relevance_score", c.get("score", 0.0)) for c in candidates], default=0.0)

        if top_score < self.threshold:
            return False, f"insufficient_retrieval_context (top score {top_score:.3f} < threshold {self.threshold})"

        return True, "sufficient_context"
