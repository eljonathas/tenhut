from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CommandSpec:
    """An external command to run."""

    argv: tuple[str, ...]
    stdin_text: str | None = None
    extra_env: dict[str, str] | None = None
    timeout: float | None = None
    cwd: Path | None = None
