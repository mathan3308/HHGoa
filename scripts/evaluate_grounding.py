import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.guardrails.grounding_guard import GroundingGuard

def evaluate_grounding():
    print("==================================================")
    print("GROUNDING GUARD VALIDATION EVALUATION")
    print("==================================================")

    guard = GroundingGuard(threshold=0.60)

    context = [
        {"text": "New Delhi is the capital of India. It houses parliament and supreme court."}
    ]

    test_cases = [
        {
            "name": "Supported Answer",
            "answer": "New Delhi is the capital of India.",
            "expected_grounded": True
        },
        {
            "name": "Hallucinated Answer",
            "answer": "Mumbai is the financial capital of India and has the largest port in Asia.",
            "expected_grounded": False
        },
        {
            "name": "Refusal Answer",
            "answer": "I couldn't find enough information in the provided dataset to answer that question.",
            "expected_grounded": False
        }
    ]

    for tc in test_cases:
        res = guard.validate(tc["answer"], context)
        status = "PASSED" if res.grounded == tc["expected_grounded"] else "FAILED"
        print(f"Test '{tc['name']}': {status} | Grounded={res.grounded} | Confidence={res.confidence} | Reason='{res.reason}'")

    print("==================================================\n")

if __name__ == "__main__":
    evaluate_grounding()
