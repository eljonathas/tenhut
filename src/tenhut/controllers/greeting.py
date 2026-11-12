from __future__ import annotations

from dataclasses import dataclass

from .reaction import Reaction


@dataclass(frozen=True, slots=True)
class Greeting:
    """What the general says on opening the app (a translation key) and how he looks saying it."""

    key: str
    reaction: Reaction
