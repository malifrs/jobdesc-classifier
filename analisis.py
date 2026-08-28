"""Analysis layer for the JobDesc Classifier web app.

This module loads the trained model bundle from a joblib file, then runs the
same analysis pipeline used during the notebook experiments: role classification
(SVM), sub-role assignment (cosine similarity), and skill extraction (O*NET
dictionary matching).
"""

from pathlib import Path
from typing import Optional, TypedDict

import joblib
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity

# Minimum input length; text shorter than this lacks enough signal to analyze.
MIN_CHARS = 30


class SubRoleResult(TypedDict):
    """Result of matching a job description to an O*NET occupation profile."""
    sub_role: Optional[str]
    onet_code: Optional[str]
    cosine_similarity: float
    ranking: list["SubRoleCandidate"]


class SubRoleCandidate(TypedDict):
    """A single ranked candidate occupation from cosine-similarity matching."""
    sub_role: str
    onet_code: str
    cosine_similarity: float


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
    sub_role: Optional[str]
    onet_code: Optional[str]
    cosine_similarity: float
    skills: list[SkillMatch]
    top_3_sub_role: list[SubRoleCandidate]
    top_3_role_margins: list[RoleMargin]


# Bundle components are a dict of trained artifacts loaded from the joblib file.
BundleComponents = dict[str, object]


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


class Classifier:
    """Wraps the trained model bundle and exposes the analysis pipeline."""

    def __init__(self, components: BundleComponents) -> None:
        self.model = components["role_model"]
        self.profiles = components["profiles"]
        self.subrole_vectorizer = components["subrole_vectorizer"]
        self.profile_matrix = components["profile_matrix"]
        self.skill_weight_by_code = components["skill_weight_by_code"]
        self.all_skill_names = components["all_skill_names"]
        self.skill_aliases = components["skill_aliases"]
        self.acronym_to_skill = components["acronym_to_skill"]
        self.metadata = components.get("metadata", {})

    def find_subrole(self, text: str, role: str) -> SubRoleResult:
        """Pick the best-matching sub-role via cosine similarity, restricted to
        occupations that belong to the predicted role category."""
        mask = (self.profiles["role_category"] == role).values
        if not mask.any():
            return {"sub_role": None, "onet_code": None, "cosine_similarity": 0.0, "ranking": []}

        similarities = cosine_similarity(
            self.subrole_vectorizer.transform([text]), self.profile_matrix[mask]
        ).ravel()

        candidates = self.profiles[mask].reset_index(drop=True)
        order = np.argsort(-similarities)
        ranking: list[SubRoleCandidate] = [
            {
                "sub_role": candidates.iloc[i]["sub_role"],
                "onet_code": candidates.iloc[i]["onet_code"],
                "cosine_similarity": round(float(similarities[i]), 4),
            }
            for i in order
        ]
        best = ranking[0]
        return {
            "sub_role": best["sub_role"],
            "onet_code": best["onet_code"],
            "cosine_similarity": best["cosine_similarity"],
            "ranking": ranking,
        }

    def extract_skills(self, text: str, onet_code: Optional[str] = None) -> list[SkillMatch]:
        """Extract skills from the text by matching the O*NET dictionary and its
        aliases. Weights come from the selected sub-role's occupation; skills
        outside that occupation are still shown with a default weight of 1."""
        normalized_text = normalize(text)
        occupation_weights = self.skill_weight_by_code.get(onet_code, {})

        def weight(skill: str) -> int:
            return int(occupation_weights.get(skill, 1))

        found: dict[str, int] = {}
        for skill in self.all_skill_names:
            aliases = [skill] + self.skill_aliases.get(skill, [])
            if any(contains_term(normalized_text, alias) for alias in aliases):
                found[skill] = weight(skill)

        for acronym, skill in self.acronym_to_skill.items():
            if contains_term(normalized_text, acronym):
                found.setdefault(skill, weight(skill))

        results: list[SkillMatch] = [{"skill": s, "weight": w} for s, w in found.items()]
        results.sort(key=lambda item: (-item["weight"], item["skill"].lower()))
        return results

    def analyze(self, description: str) -> AnalysisResult:
        """Run the full analysis pipeline on a single job description."""
        text = str(description).strip()
        if len(text) < MIN_CHARS:
            raise ValueError(f"Job description must be at least {MIN_CHARS} characters.")

        role = str(self.model.predict([text])[0])

        # Decision-function margins are used to rank role candidates. These are
        # not probabilities, so they are never shown to the user.
        margins = np.asarray(self.model.decision_function([text])).ravel()
        role_ranking: list[RoleMargin] = sorted(
            (
                {"role": str(label), "margin": round(float(score), 4)}
                for label, score in zip(self.model.classes_, margins)
            ),
            key=lambda item: item["margin"],
            reverse=True,
        )

        subrole = self.find_subrole(text, role)
        skills = self.extract_skills(text, subrole["onet_code"])

        return {
            "main_role": role,
            "sub_role": subrole["sub_role"],
            "onet_code": subrole["onet_code"],
            "cosine_similarity": subrole["cosine_similarity"],
            "skills": skills,
            "top_3_sub_role": subrole["ranking"][:3],
            "top_3_role_margins": role_ranking[:3],
        }


def find_bundle(bundle_path: Optional[str] = None) -> Path:
    """Locate the joblib model bundle in common locations relative to this file."""
    if bundle_path:
        return Path(bundle_path)

    base = Path(__file__).resolve().parent
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


def load_classifier(bundle_path: Optional[str] = None) -> Classifier:
    """Load the model bundle from disk and wrap it into a Classifier instance."""
    return Classifier(joblib.load(find_bundle(bundle_path)))
