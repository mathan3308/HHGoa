import base64
import io

def encode_audio_base64(audio_bytes: bytes) -> str:
    """Encodes raw audio byte array into base64 string for API payloads."""
    return base64.b64encode(audio_bytes).decode('utf-8')

def decode_audio_base64(b64_string: str) -> bytes:
    """Decodes base64 string back into raw audio bytes."""
    return base64.b64decode(b64_string)
