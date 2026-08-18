from typing import Tuple

UNSAFE_KEYWORDS = ["explicit_violence", "illegal_act", "hate_speech_flag"]

class SafetyGuard:
    """Tier 3: Safety Guard checking for offensive or unsafe content."""
    def validate(self, text: str) -> Tuple[bool, str]:
        text_lower = text.lower()
        for kw in UNSAFE_KEYWORDS:
            if kw in text_lower:
                return False, "unsafe_content_detected"
        return True, "safe"
