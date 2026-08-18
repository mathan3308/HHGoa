import logging
import sys
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str = "voice_rag"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _sanitize(self, message: str) -> str:
        # Prevent leaking raw API keys if accidentally passed
        for secret in ["SARVAM_API_KEY", "QDRANT_API_KEY", "Bearer "]:
            if secret in message:
                message = message.replace(secret, "[REDACTED]")
        return message

    def info(self, message: str, request_id: str = None, **kwargs):
        prefix = f"[{request_id}] " if request_id else ""
        extra = f" | {json.dumps(kwargs)}" if kwargs else ""
        self.logger.info(f"{prefix}{self._sanitize(message)}{extra}")

    def warning(self, message: str, request_id: str = None, **kwargs):
        prefix = f"[{request_id}] " if request_id else ""
        extra = f" | {json.dumps(kwargs)}" if kwargs else ""
        self.logger.warning(f"{prefix}{self._sanitize(message)}{extra}")

    def error(self, message: str, request_id: str = None, **kwargs):
        prefix = f"[{request_id}] " if request_id else ""
        extra = f" | {json.dumps(kwargs)}" if kwargs else ""
        self.logger.error(f"{prefix}{self._sanitize(message)}{extra}")

logger = StructuredLogger()
