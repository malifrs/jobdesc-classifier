"""Shared text-processing helpers used across analysis components."""

import re


def normalize(text: str) -> str:
    """Lowercase the text and collapse all whitespace runs into single spaces."""
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def contains_term(text: str, term: str) -> bool:
    """Check whether `term` appears as a whole word in `text` (no partial matches).

    Short terms are blocked ONLY when they are purely alphanumeric (e.g. "go",
    "ai", "os") because they easily collide with common words; symbolic names
    like "c#" or "c++" are still allowed because they are distinctive enough.
    """
    normalized_term = normalize(term)
    if not normalized_term:
        return False
    if len(normalized_term) < 3 and normalized_term.isalnum():
        return False
    pattern = r"(?<![a-z0-9])" + re.escape(normalized_term) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None
