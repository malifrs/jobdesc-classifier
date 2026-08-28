"""Backward-compatibility facade — re-exports from the core package.

Existing code that imports from `analisis` (e.g. notebooks) will still work.
New code should import directly from `core` instead.
"""

from core import (
    MIN_CHARS,
    AnalysisResult,
    JobDescriptionAnalyzer,
    create_analyzer,
    find_bundle,
    load_bundle,
)

# Alias for backward compatibility — returns a JobDescriptionAnalyzer (same .analyze() API).
load_classifier = create_analyzer

__all__ = [
    "MIN_CHARS",
    "AnalysisResult",
    "JobDescriptionAnalyzer",
    "create_analyzer",
    "find_bundle",
    "load_bundle",
    "load_classifier",
]
