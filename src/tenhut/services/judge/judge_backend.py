from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ...core import Clock, JudgeSettings, Settings
from .judge_request import JudgeRequest
from .verdict import Verdict


class JudgeBackend(ABC):
    """Decides a request. Implementations: Claude, Codex and the local (no AI) judge."""

    name_key: str
    uses_ai = True

    def __init__(self, settings: Settings, *, clock: Clock, work_dir: Path | None = None) -> None:
        self._settings = settings
        self._clock = clock
        self._work_dir = work_dir

    @property
    def options(self) -> JudgeSettings:
        return self._settings.judge

    @abstractmethod
    def available(self) -> bool:
        """Is this judge's tool installed?"""

    @abstractmethod
    def ask(self, request: JudgeRequest) -> Verdict:
        """The verdict for `request`; may take long, so run it in a JudgeJob. Never raises."""
