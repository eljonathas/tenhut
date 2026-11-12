from __future__ import annotations

from tenhut import i18n
from tenhut.i18n import t

from .choice_editor import ChoiceEditor


class LanguageEditor(ChoiceEditor):
    """The interface language; each choice is shown by its own name."""

    def __init__(self) -> None:
        super().__init__(list(i18n.LANGS))

    def shown(self, value: object) -> str:
        return t(i18n.LANG_NAME[value]) if value in i18n.LANG_NAME else str(value)
