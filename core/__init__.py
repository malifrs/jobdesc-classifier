"""Core analysis package — re-exports the public API.

Importing from `core` gives you everything you need:
    from core import create_analyzer, MIN_CHARS, AnalysisResult
"""

from .analyzer import MIN_CHARS, JobDescriptionAnalyzer
from .bundle import create_analyzer, find_bundle, load_bundle
from .interfaces import IJobAnalyzer, IRoleClassifier, ISkillExtractor, ISubRoleMatcher
from .models import (
    AnalysisResult,
    BundleComponents,
    RoleMargin,
    SkillMatch,
    SubRoleCandidate,
    SubRoleResult,
)
from .role_classifier import SVMRoleClassifier
from .skill_extractor import OnetSkillExtractor
from .subrole_matcher import CosineSubRoleMatcher

__all__ = [
    "MIN_CHARS",
    "JobDescriptionAnalyzer",
    "create_analyzer",
    "find_bundle",
    "load_bundle",
    "IJobAnalyzer",
    "IRoleClassifier",
    "ISkillExtractor",
    "ISubRoleMatcher",
    "AnalysisResult",
    "BundleComponents",
    "RoleMargin",
    "SkillMatch",
    "SubRoleCandidate",
    "SubRoleResult",
    "SVMRoleClassifier",
    "OnetSkillExtractor",
    "CosineSubRoleMatcher",
]
