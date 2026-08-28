"""Data contracts (TypedDicts) for the analysis pipeline.

Think of these like TypeScript interfaces — they describe the shape of the data
that flows between the different analysis components.
"""

from typing import TypedDict


class SubRoleCandidate(TypedDict):
    """A single ranked candidate occupation from cosine-similarity matching."""
    sub_role: str
    onet_code: str
    cosine_similarity: float


class SubRoleResult(TypedDict):
    """Result of matching a job description to an O*NET occupation profile."""
    sub_role: str | None
    onet_code: str | None
    cosine_similarity: float
    ranking: list[SubRoleCandidate]


class SkillMatch(TypedDict):
    """A skill recognized in the text along with its occupation weight."""
    skill: str
    weight: int


class RoleMargin(TypedDict):
    """A ranked role candidate from the SVM decision-function scores."""
    role: str
    margin: float


class AnalysisResult(TypedDict):
    """Full output of analyzing one job description."""
    main_role: str
    sub_role: str | None
    onet_code: str | None
    cosine_similarity: float
    skills: list[SkillMatch]
    top_3_sub_role: list[SubRoleCandidate]
    top_3_role_margins: list[RoleMargin]


# Bundle components are a dict of trained artifacts loaded from the joblib file.
BundleComponents = dict[str, object]
