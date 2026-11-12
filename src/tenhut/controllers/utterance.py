from __future__ import annotations

from dataclasses import dataclass

from .reaction import Reaction


@dataclass(frozen=True, slots=True)
class Utterance:
    """Something the general says: the words, how he looks while saying it and for how long he keeps that look."""

    message: str
    reaction: Reaction | None = None
    seconds: float = 4.0
    persist: bool = False
