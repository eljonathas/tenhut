from __future__ import annotations

from dataclasses import dataclass

from tenhut.game.painting import Rgb


@dataclass(frozen=True, slots=True)
class StampContent:
    message: str
    color: Rgb
