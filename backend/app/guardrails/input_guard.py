import re
from typing import Tuple

BLOCKED_PATTERNS = [
    r'ignore previous instructions',
    r'system prompt',
    r'override guardrails',
    r'hack',
    r'jailbreak',
    r'bypass',
]

class InputGuard:
    """Tier 1: Input Safety & Prompt Injection Check."""
    def validate(self, text: str) -> Tuple[bool, str]:
        if not text or not text.strip():
            return False, "Input query is empty."

        clean_text = text.lower()
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, clean_text):
                return False, f"Input contained prohibited directive or prompt injection attempt."

        return True, "valid"
