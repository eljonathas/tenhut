from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from tenhut.i18n import t

from .editor_kind import EditorKind


class RowEditor(ABC):
    """How one settings row changes its value when a control is clicked, and how the value reads."""

    kind: ClassVar[EditorKind] = EditorKind.STEPPER

    @abstractmethod
    def adjust(self, current: object, direction: int) -> object:
        """The value after a click on the minus (-1) or plus (+1) control."""

    def shown(self, value: object) -> str:
        return t("settings.value.default") if value == "" else str(value)
