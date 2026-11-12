from __future__ import annotations

from dataclasses import dataclass

from .judge_preference import JudgePreference
from .number_rule import NumberRule
from .setting_value import SettingValue


@dataclass(frozen=True, slots=True)
class JudgeSettings:
    """How requests are judged and how much a granted pass may give."""

    preference: JudgePreference = JudgePreference.AUTO
    claude_binary: str = "claude"
    claude_model: str = "haiku"
    codex_binary: str = "codex"
    codex_model: str = ""
    local_wait_seconds: int = 60
    timeout_seconds: int = 90
    max_grant_minutes: int = 15
    denial_cooldown_seconds: int = 120

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> JudgeSettings:
        d = cls()
        return cls(
            JudgePreference.parse(data.get("judge"), d.preference),
            SettingValue.text(data.get("claude_binary"), d.claude_binary),
            SettingValue.text(data.get("claude_model"), d.claude_model),
            SettingValue.text(data.get("codex_binary"), d.codex_binary),
            SettingValue.text(data.get("codex_model"), d.codex_model),
            NumberRule(d.local_wait_seconds, 0, 3600).integer(data.get("local_wait_seconds")),
            NumberRule(d.timeout_seconds, 5, 900).integer(data.get("judge_timeout_seconds")),
            NumberRule(d.max_grant_minutes, 1, 240).integer(data.get("max_grant_minutes")),
            NumberRule(d.denial_cooldown_seconds, 0, 3600).integer(data.get("denial_cooldown_seconds")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "judge": self.preference.value,
            "claude_binary": self.claude_binary,
            "claude_model": self.claude_model,
            "codex_binary": self.codex_binary,
            "codex_model": self.codex_model,
            "local_wait_seconds": self.local_wait_seconds,
            "judge_timeout_seconds": self.timeout_seconds,
            "max_grant_minutes": self.max_grant_minutes,
            "denial_cooldown_seconds": self.denial_cooldown_seconds,
        }
