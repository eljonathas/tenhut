from __future__ import annotations

from tenhut.ui.widgets.balloon import Balloon

from .tickable import Tickable


class BalloonTicker(Tickable):
    """Advances the speech balloon every frame."""

    def __init__(self, balloon: Balloon) -> None:
        self._balloon = balloon

    def tick(self, dt: float) -> None:
        self._balloon.update(dt)
