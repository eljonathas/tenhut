from __future__ import annotations

from dataclasses import dataclass

from tenhut.game.painting import Rgb


@dataclass(frozen=True, slots=True)
class Heading:
    """The title at the top of a page and its colour."""

    message: str
    color: Rgb
