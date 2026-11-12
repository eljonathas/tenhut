from __future__ import annotations

from dataclasses import dataclass

from .severity import Severity


@dataclass(frozen=True, slots=True)
class StatusLine:
    """One line of the status area of the board (or the note in the mini HUD)."""

    text: str
    severity: Severity
