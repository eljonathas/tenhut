from __future__ import annotations

from .row_editor import RowEditor


class ChoiceEditor(RowEditor):
    """An option picked from a fixed list; the controls cycle through it."""

    def __init__(self, options: list[str]) -> None:
        self._options = options

    def adjust(self, current: object, direction: int) -> object:
        if current not in self._options:
            return self._options[0]
        return self._options[(self._options.index(current) + direction) % len(self._options)]
