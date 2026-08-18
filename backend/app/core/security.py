from fastapi import UploadFile
from backend.app.core.exceptions import InvalidAudioException

ALLOWED_AUDIO_TYPES = {
    "audio/wav", "audio/x-wav", "audio/mp3", "audio/mpeg", 
    "audio/m4a", "audio/x-m4a", "audio/webm", "audio/ogg",
    "audio/aac", "application/octet-stream"
}

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

def validate_audio_file(file: UploadFile, contents: bytes) -> None:
    """Validates the uploaded audio file format and size."""
    if not contents or len(contents) == 0:
        raise InvalidAudioException("Uploaded audio file is empty.")

    if len(contents) > MAX_AUDIO_SIZE_BYTES:
        raise InvalidAudioException(f"Audio file exceeds maximum allowed size of {MAX_AUDIO_SIZE_BYTES // (1024*1024)}MB.")

    content_type = (file.content_type or "").lower()
    file_ext = (file.filename or "").split(".")[-1].lower()

    valid_extensions = {"wav", "mp3", "m4a", "webm", "ogg", "aac", "flac"}

    if content_type not in ALLOWED_AUDIO_TYPES and file_ext not in valid_extensions:
        raise InvalidAudioException(
            f"Unsupported audio format '{content_type}'. Allowed extensions: {', '.join(valid_extensions)}"
        )
