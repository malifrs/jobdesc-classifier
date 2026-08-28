"""Cosine-similarity sub-role matcher — finds the best O*NET occupation (Single Responsibility)."""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .interfaces import ISubRoleMatcher
from .models import SubRoleCandidate, SubRoleResult


class CosineSubRoleMatcher(ISubRoleMatcher):
    """Matches a job description to O*NET sub-roles using cosine similarity."""

    def __init__(self, profiles: object, vectorizer: object, profile_matrix: object) -> None:
        self._profiles = profiles
        self._vectorizer = vectorizer
        self._profile_matrix = profile_matrix

    def match(self, text: str, role: str) -> SubRoleResult:
        """Pick the best-matching sub-role via cosine similarity within the predicted role."""
        mask = (self._profiles["role_category"] == role).values
        if not mask.any():
            return {"sub_role": None, "onet_code": None, "cosine_similarity": 0.0, "ranking": []}

        similarities = cosine_similarity(
            self._vectorizer.transform([text]), self._profile_matrix[mask]
        ).ravel()

        candidates = self._profiles[mask].reset_index(drop=True)
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
