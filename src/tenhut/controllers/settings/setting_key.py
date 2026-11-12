from __future__ import annotations

from enum import Enum


class SettingKey(Enum):
    """Every option the settings page edits; the value is where it sits in the settings dictionary."""

    LANGUAGE = ("language",)
    WORK_MINUTES = ("work_minutes",)
    SHORT_BREAK_MINUTES = ("short_break_minutes",)
    LONG_BREAK_MINUTES = ("long_break_minutes",)
    CYCLES_BEFORE_LONG_BREAK = ("cycles_before_long_break",)
    MAX_GRANT_MINUTES = ("max_grant_minutes",)
    JUDGE = ("judge",)
    CLAUDE_MODEL = ("claude_model",)
    CODEX_MODEL = ("codex_model",)
    LOCAL_WAIT_SECONDS = ("local_wait_seconds",)
    SOUND_ENABLED = ("sound_enabled",)
    VOLUME = ("volume",)
    CLOSE_BLOCKED_APPS = ("close_blocked_apps",)
    CAMERA_ENABLED = ("camera", "enabled")
    CAMERA_TOLERANCE = ("camera", "tolerance_seconds")
    CAMERA_PENALTY = ("camera", "penalty_minutes")

    @property
    def path(self) -> tuple[str, ...]:
        return self.value

    @property
    def always_unlocked(self) -> bool:
        """Options that cannot help dodge the focus rules stay editable during a combat."""
        return self in (SettingKey.SOUND_ENABLED, SettingKey.VOLUME, SettingKey.LANGUAGE)
