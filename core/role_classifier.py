"""SVM-based role classifier — predicts the main job category (Single Responsibility)."""

import numpy as np

from .interfaces import IRoleClassifier
from .models import RoleMargin


class SVMRoleClassifier(IRoleClassifier):
    """Classifies a job description into a role category using a trained SVM."""

    def __init__(self, model: object) -> None:
        self._model = model

    def classify(self, text: str) -> tuple[str, list[RoleMargin]]:
        """Predict the role and rank all candidates by decision-function margin."""
        role = str(self._model.predict([text])[0])

        # Decision-function margins are used to rank role candidates. These are
        # not probabilities, so they are never shown to the user.
        margins = np.asarray(self._model.decision_function([text])).ravel()
        ranking: list[RoleMargin] = sorted(
            (
                {"role": str(label), "margin": round(float(score), 4)}
                for label, score in zip(self._model.classes_, margins)
            ),
            key=lambda item: item["margin"],
            reverse=True,
        )
        return role, ranking
