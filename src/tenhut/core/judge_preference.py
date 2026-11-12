from __future__ import annotations

from enum import Enum


class JudgePreference(Enum):
    """Which judge the user wants; AUTO tries Claude, then Codex, then falls back to the local judge."""

    AUTO = "auto"
    CLAUDE = "claude"
    CODEX = "codex"
    NONE = "none"

    @classmethod
    def parse(cls, value: object, default: JudgePreference) -> JudgePreference:
        try:
            return cls(value)
        except ValueError:
            return default
