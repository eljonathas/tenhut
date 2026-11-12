from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import ClassVar

from tenhut.i18n import t
from tenhut.services.judge import ClaudeJudge, CodexJudge, JudgeBackend, JudgeFactory

from .choice_editor import ChoiceEditor
from .judge_editor import JudgeEditor
from .language_editor import LanguageEditor
from .number_editor import NumberEditor
from .number_range import NumberRange
from .setting_key import SettingKey
from .setting_row import SettingRow
from .settings_draft import SettingsDraft
from .toggle_editor import ToggleEditor

RowBuilder = Callable[[SettingsDraft], list[SettingRow]]


class SettingsRowCatalog:
    """The rows of the settings page; the judge's model row follows the tool that will really be used."""

    WORK_MINUTES = NumberRange(5, 5, 120)
    SHORT_BREAK_MINUTES = NumberRange(1, 1, 30)
    LONG_BREAK_MINUTES = NumberRange(5, 5, 60)
    CYCLES = NumberRange(1, 2, 8)
    GRANT_MINUTES = NumberRange(1, 1, 60)
    VOLUME = NumberRange(10, 0, 100)
    TOLERANCE = NumberRange(1, 3, 30)
    PENALTY = NumberRange(1, 0, 10)
    LOCAL_WAIT = NumberRange(10, 10, 300)
    CLAUDE_MODELS: ClassVar[list[str]] = ["haiku", "sonnet", "opus"]
    EXPLICIT_PREFERENCES = ("claude", "codex")

    def __init__(self, factory: JudgeFactory, work_dir: Path) -> None:
        self._factory = factory
        self._work_dir = work_dir
        self._judge_rows: dict[type[JudgeBackend], RowBuilder] = {
            ClaudeJudge: self._claude_rows,
            CodexJudge: self._codex_rows,
        }

    def rows(self, draft: SettingsDraft) -> list[SettingRow]:
        return [*self._timer_rows(), *self._judge_rows_for(draft), *self._behaviour_rows()]

    def _timer_rows(self) -> list[SettingRow]:
        return [
            SettingRow(t("settings.row.language"), SettingKey.LANGUAGE, LanguageEditor()),
            SettingRow(t("settings.row.work_minutes"), SettingKey.WORK_MINUTES, NumberEditor(self.WORK_MINUTES)),
            SettingRow(
                t("settings.row.short_break_minutes"),
                SettingKey.SHORT_BREAK_MINUTES,
                NumberEditor(self.SHORT_BREAK_MINUTES),
            ),
            SettingRow(
                t("settings.row.long_break_minutes"),
                SettingKey.LONG_BREAK_MINUTES,
                NumberEditor(self.LONG_BREAK_MINUTES),
            ),
            SettingRow(
                t("settings.row.cycles_until_long_break"),
                SettingKey.CYCLES_BEFORE_LONG_BREAK,
                NumberEditor(self.CYCLES),
            ),
            SettingRow(
                t("settings.row.max_pass_minutes"), SettingKey.MAX_GRANT_MINUTES, NumberEditor(self.GRANT_MINUTES)
            ),
        ]

    def _behaviour_rows(self) -> list[SettingRow]:
        return [
            SettingRow(t("settings.row.sounds"), SettingKey.SOUND_ENABLED, ToggleEditor()),
            SettingRow(t("settings.row.volume"), SettingKey.VOLUME, NumberEditor(self.VOLUME)),
            SettingRow(t("settings.row.kill_blocked_apps"), SettingKey.CLOSE_BLOCKED_APPS, ToggleEditor()),
            SettingRow(t("settings.row.camera_surveillance"), SettingKey.CAMERA_ENABLED, ToggleEditor()),
            SettingRow(
                t("settings.row.camera_tolerance_seconds"), SettingKey.CAMERA_TOLERANCE, NumberEditor(self.TOLERANCE)
            ),
            SettingRow(t("settings.row.camera_penalty_minutes"), SettingKey.CAMERA_PENALTY, NumberEditor(self.PENALTY)),
        ]

    def _judge_rows_for(self, draft: SettingsDraft) -> list[SettingRow]:
        backend = self._factory.create(draft.as_settings(), self._work_dir)
        preference = draft.get(SettingKey.JUDGE)
        first = SettingRow(self._judge_label(str(preference), backend), SettingKey.JUDGE, JudgeEditor())
        return [first, *self._judge_rows.get(type(backend), self._local_rows)(draft)]

    @classmethod
    def _judge_label(cls, preference: str, backend: JudgeBackend) -> str:
        if preference in cls.EXPLICIT_PREFERENCES and not backend.uses_ai:
            return t("settings.row.judge_missing", pref=preference)
        if preference == "auto":
            return t("settings.row.judge_auto", name=t(backend.name_key))
        return t("settings.row.judge")

    def _claude_rows(self, draft: SettingsDraft) -> list[SettingRow]:
        return [SettingRow(t("settings.row.claude_model"), SettingKey.CLAUDE_MODEL, ChoiceEditor(self.CLAUDE_MODELS))]

    def _codex_rows(self, draft: SettingsDraft) -> list[SettingRow]:
        # empty = Codex's default model; another model can be put in "codex_model" in the JSON
        custom = draft.get(SettingKey.CODEX_MODEL)
        options = ["", *([str(custom)] if custom else [])]
        return [SettingRow(t("settings.row.codex_model"), SettingKey.CODEX_MODEL, ChoiceEditor(options))]

    def _local_rows(self, draft: SettingsDraft) -> list[SettingRow]:
        return [
            SettingRow(
                t("settings.row.no_ai_wait_seconds"), SettingKey.LOCAL_WAIT_SECONDS, NumberEditor(self.LOCAL_WAIT)
            )
        ]
