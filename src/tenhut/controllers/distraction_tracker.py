from __future__ import annotations


class DistractionTracker:
    """Remembers whether the general was looking at the scenery, to catch the moment he turns back."""

    def __init__(self) -> None:
        self._was_distracted = False

    @property
    def was_distracted(self) -> bool:
        return self._was_distracted

    def notice(self) -> None:
        self._was_distracted = True

    def forget(self) -> None:
        self._was_distracted = False
