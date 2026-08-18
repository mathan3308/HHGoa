import re
from typing import List

def normalize_text(text: str) -> str:
    """Normalizes whitespace and strips control characters from text."""
    if not text:
        return ""
    # Strip non-printable ASCII/Unicode control characters except newline
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences using regex boundary matching for multiple scripts."""
    if not text:
        return []
    text = normalize_text(text)
    # Split by standard sentence end markers (. ! ? and Devanagari/Indic danda ।)
    sentence_endings = re.compile(r'(?<=[.!?।])\s+')
    sentences = sentence_endings.split(text)
    return [s.strip() for s in sentences if s.strip()]

def word_tokenize(text: str) -> List[str]:
    """Basic whitespace and punctuation tokenizer."""
    return re.findall(r'\w+', text.lower())
