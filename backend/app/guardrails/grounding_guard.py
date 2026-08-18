from typing import List, Dict, Any
from backend.app.models.response_models import GroundingResult

REFUSAL_PHRASE = "I couldn't find enough information in the provided dataset to answer that question."

class GroundingGuard:
    """
    Tier 4: Grounding Validator.
    Validates whether the generated answer is strictly grounded in retrieved context passages.
    """
    def __init__(self, threshold: float = 0.60):
        self.threshold = threshold

    def validate(self, answer: str, context_passages: List[Dict[str, Any]]) -> GroundingResult:
        if not answer or answer.strip() == REFUSAL_PHRASE:
            return GroundingResult(
                grounded=False,
                reason="Refusal phrase returned due to insufficient context.",
                confidence=1.0
            )

        if not context_passages:
            return GroundingResult(
                grounded=False,
                reason="No retrieved context passages provided.",
                confidence=0.0
            )

        # Calculate word overlap ratio between answer words and combined context text
        context_text = " ".join([c.get("text", "") for c in context_passages]).lower()
        answer_words = [w for w in answer.lower().split() if len(w) > 3]

        if not answer_words:
            return GroundingResult(grounded=True, reason="Short response supported.", confidence=0.9)

        supported_count = sum(1 for word in answer_words if word in context_text)
        overlap_ratio = supported_count / len(answer_words)

        if overlap_ratio >= self.threshold:
            return GroundingResult(
                grounded=True,
                reason="Answer factual claims align with retrieved context.",
                confidence=round(overlap_ratio, 2)
            )
        else:
            return GroundingResult(
                grounded=False,
                reason=f"Answer overlap ({overlap_ratio:.2f}) below grounding threshold ({self.threshold}).",
                confidence=round(overlap_ratio, 2)
            )
