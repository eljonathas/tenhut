from __future__ import annotations


class TaskScroll:
    """How far the task list has been scrolled, shared by every page that lists tasks."""

    def __init__(self) -> None:
        self._offset = 0

    @property
    def offset(self) -> int:
        return self._offset

    def by(self, rows: int) -> None:
        """Scrolls up for a positive ``rows`` (the wheel's direction)."""
        self._offset = max(0, self._offset - rows)

    def clamp(self, total: int, visible: int) -> int:
        self._offset = max(0, min(self._offset, max(0, total - visible)))
        return self._offset
