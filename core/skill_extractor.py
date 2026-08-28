"""O*NET skill extractor — finds skills mentioned in a job description (Single Responsibility)."""

from .interfaces import ISkillExtractor
from .models import SkillMatch
from .text_utils import contains_term, normalize


class OnetSkillExtractor(ISkillExtractor):
    """Extracts skills from text by matching the O*NET dictionary and its aliases."""

    def __init__(
        self,
        skill_weight_by_code: dict,
        all_skill_names: list,
        skill_aliases: dict,
        acronym_to_skill: dict,
    ) -> None:
        self._skill_weight_by_code = skill_weight_by_code
        self._all_skill_names = all_skill_names
        self._skill_aliases = skill_aliases
        self._acronym_to_skill = acronym_to_skill

    def extract(self, text: str, onet_code: str | None = None) -> list[SkillMatch]:
        """Match the O*NET dictionary against the text and return weighted skills."""
        normalized_text = normalize(text)
        occupation_weights = self._skill_weight_by_code.get(onet_code, {})

        def weight(skill: str) -> int:
            return int(occupation_weights.get(skill, 1))

        found: dict[str, int] = {}
        for skill in self._all_skill_names:
            aliases = [skill] + self._skill_aliases.get(skill, [])
            if any(contains_term(normalized_text, alias) for alias in aliases):
                found[skill] = weight(skill)

        for acronym, skill in self._acronym_to_skill.items():
            if contains_term(normalized_text, acronym):
                found.setdefault(skill, weight(skill))

        results: list[SkillMatch] = [{"skill": s, "weight": w} for s, w in found.items()]
        results.sort(key=lambda item: (-item["weight"], item["skill"].lower()))
        return results
