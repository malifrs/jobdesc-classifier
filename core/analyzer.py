"""Job description analyzer — orchestrates the full pipeline (Dependency Inversion).

This class depends only on abstractions (IRoleClassifier, ISubRoleMatcher,
ISkillExtractor), never on concrete implementations. New classifiers, matchers,
or extractors can be injected without changing this class (Open/Closed +
Dependency Inversion).
"""

from .interfaces import IJobAnalyzer, IRoleClassifier, ISkillExtractor, ISubRoleMatcher
from .models import AnalysisResult

# Minimum input length; text shorter than this lacks enough signal to analyze.
MIN_CHARS = 30


class JobDescriptionAnalyzer(IJobAnalyzer):
    """Orchestrates role classification, sub-role matching, and skill extraction."""

    def __init__(
        self,
        role_classifier: IRoleClassifier,
        subrole_matcher: ISubRoleMatcher,
        skill_extractor: ISkillExtractor,
    ) -> None:
        self._role_classifier = role_classifier
        self._subrole_matcher = subrole_matcher
        self._skill_extractor = skill_extractor

    def analyze(self, description: str) -> AnalysisResult:
        """Run the full analysis pipeline on a single job description."""
        text = str(description).strip()
        if len(text) < MIN_CHARS:
            raise ValueError(f"Job description must be at least {MIN_CHARS} characters.")

        role, role_margins = self._role_classifier.classify(text)
        subrole = self._subrole_matcher.match(text, role)
        skills = self._skill_extractor.extract(text, subrole["onet_code"])

        return {
            "main_role": role,
            "sub_role": subrole["sub_role"],
            "onet_code": subrole["onet_code"],
            "cosine_similarity": subrole["cosine_similarity"],
            "skills": skills,
            "top_3_sub_role": subrole["ranking"][:3],
            "top_3_role_margins": role_margins[:3],
        }
