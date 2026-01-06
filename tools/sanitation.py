# sanitation.py
# this is to sanitize user inputs
import os

def sanitize(text: str, *, length_min: int = 1, length_max: int = 50) -> str | None:
    
    text = text.strip()  # remove extra whitespace
    text = text.lower()  # normalize
    if not (length_min <= len(text) <= length_max):
        return None

    forbidden = [';', '--', '"', "'"]  # no little bobby tables
    for ch in forbidden:
        text = text.replace(ch, '')
    return text if text else None