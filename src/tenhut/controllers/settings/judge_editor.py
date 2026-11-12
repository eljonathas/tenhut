from __future__ import annotations

from tenhut.core import JudgePreference
from tenhut.i18n import t

from .choice_editor import ChoiceEditor


class JudgeEditor(ChoiceEditor):
    """Which judge decides the requests."""

    def __init__(self) -> None:
        super().__init__([preference.value for preference in JudgePreference])

    def shown(self, value: object) -> str:
        if value == JudgePreference.NONE.value:
            return t("settings.value.none")
        return super().shown(value)
