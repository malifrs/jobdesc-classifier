"""Bundle loading and analyzer factory (Dependency Inversion wiring point).

This module is the only place that knows about concrete implementations. It
loads the joblib bundle and wires the concrete classes into the orchestrator.
Everything else depends on abstractions.
"""

from pathlib import Path

import joblib

from .analyzer import JobDescriptionAnalyzer
from .models import BundleComponents
from .role_classifier import SVMRoleClassifier
from .skill_extractor import OnetSkillExtractor
from .subrole_matcher import CosineSubRoleMatcher


def find_bundle(bundle_path: str | None = None) -> Path:
    """Locate the joblib model bundle in common locations relative to this package."""
    if bundle_path:
        return Path(bundle_path)

    # Go up two levels: bundle.py → core/ → project root
    base = Path(__file__).resolve().parent.parent
    candidates = [
        base / "job_role_onet_complete.joblib",
        base.parent / "svm_onet_bright_outlook_output" / "job_role_onet_complete.joblib",
        base / "svm_onet_bright_outlook_output" / "job_role_onet_complete.joblib",
    ]
    for file in candidates:
        if file.exists():
            return file
    raise FileNotFoundError(
        "File job_role_onet_complete.joblib was not found. Run the notebook first "
        "or copy that file into the app folder."
    )


def load_bundle(bundle_path: str | None = None) -> BundleComponents:
    """Load the joblib bundle from disk and return its components as a dict."""
    return joblib.load(find_bundle(bundle_path))


def create_analyzer(bundle_path: str | None = None) -> JobDescriptionAnalyzer:
    """Load the bundle and construct a fully-wired JobDescriptionAnalyzer (factory)."""
    components = load_bundle(bundle_path)

    role_classifier = SVMRoleClassifier(components["role_model"])
    subrole_matcher = CosineSubRoleMatcher(
        components["profiles"],
        components["subrole_vectorizer"],
        components["profile_matrix"],
    )
    skill_extractor = OnetSkillExtractor(
        components["skill_weight_by_code"],
        components["all_skill_names"],
        components["skill_aliases"],
        components["acronym_to_skill"],
    )

    return JobDescriptionAnalyzer(role_classifier, subrole_matcher, skill_extractor)
