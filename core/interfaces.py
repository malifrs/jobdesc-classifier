"""Abstract contracts for each analysis step (Interface Segregation + Open/Closed).

These define the interface — like a TypeScript interface — that each component
must implement. The orchestrator depends on these abstractions, not on concrete
classes, so any new implementation can be plugged in without modifying the
orchestrator (Open/Closed + Dependency Inversion).
"""

from abc import ABC, abstractmethod

from .models import AnalysisResult, RoleMargin, SkillMatch, SubRoleResult


class IRoleClassifier(ABC):
    """Contract for predicting the main job role from a description."""

    @abstractmethod
    def classify(self, text: str) -> tuple[str, list[RoleMargin]]:
        """Return the predicted role and a ranked list of role candidates."""
        ...


class ISubRoleMatcher(ABC):
    """Contract for matching a description to an O*NET sub-role."""

    @abstractmethod
    def match(self, text: str, role: str) -> SubRoleResult:
        """Return the best-matching sub-role within the given role category."""
        ...


class ISkillExtractor(ABC):
    """Contract for extracting skills from a job description."""

    @abstractmethod
    def extract(self, text: str, onet_code: str | None) -> list[SkillMatch]:
        """Return the list of skills found in the text, sorted by weight."""
        ...


class IJobAnalyzer(ABC):
    """Contract for the full analysis pipeline (role + sub-role + skills)."""

    @abstractmethod
    def analyze(self, description: str) -> AnalysisResult:
        """Run the complete analysis on a single job description."""
        ...
