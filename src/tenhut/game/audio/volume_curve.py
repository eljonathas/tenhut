from __future__ import annotations


class VolumeCurve:
    """Maps the 0..100 master setting to a mixer level; the exponent makes the quiet steps finer."""

    def __init__(self, exponent: float = 1.5) -> None:
        self._exponent = exponent

    def level(self, percent: int) -> float:
        return (percent / 100) ** self._exponent
