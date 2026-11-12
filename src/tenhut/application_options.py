from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApplicationOptions:
    """How the application is started: ``dry_run`` only logs what would be blocked, ``headless`` makes no sound."""

    dry_run: bool = False
    headless: bool = False
