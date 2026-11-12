from __future__ import annotations

from typing import ClassVar

from .editor_kind import EditorKind
from .row_editor import RowEditor


class ToggleEditor(RowEditor):
    """A yes/no option."""

    kind: ClassVar[EditorKind] = EditorKind.TOGGLE

    def adjust(self, current: object, direction: int) -> object:
        return not current
