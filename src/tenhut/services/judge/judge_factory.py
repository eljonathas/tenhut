from __future__ import annotations

from pathlib import Path

from ...core import Clock, JudgePreference, Settings
from ..platform import CommandRunner
from .claude_judge import ClaudeJudge
from .codex_judge import CodexJudge
from .judge_backend import JudgeBackend
from .local_judge import LocalJudge


class JudgeFactory:
    """Chooses the judge from the settings: the preferred one if installed, else the local judge."""

    def __init__(self, runner: CommandRunner, clock: Clock) -> None:
        self._runner = runner
        self._clock = clock

    def create(self, settings: Settings, work_dir: Path | None = None) -> JudgeBackend:
        claude = ClaudeJudge(settings, self._runner, clock=self._clock, work_dir=work_dir)
        codex = CodexJudge(settings, self._runner, clock=self._clock, work_dir=work_dir)
        order = {
            JudgePreference.AUTO: [claude, codex],
            JudgePreference.CLAUDE: [claude],
            JudgePreference.CODEX: [codex],
            JudgePreference.NONE: [],
        }[settings.judge.preference]
        chosen = next((judge for judge in order if judge.available()), None)
        return chosen or LocalJudge(settings, clock=self._clock, work_dir=work_dir)
