from __future__ import annotations

from abc import abstractmethod
from pathlib import Path

from ...core import Clock, Settings
from ...i18n import t
from ..platform import CommandRunner
from .judge_backend import JudgeBackend
from .judge_error import JudgeError
from .judge_prompts import JudgePrompts
from .judge_request import JudgeRequest
from .judge_timeout_error import JudgeTimeoutError
from .request_kind import RequestKind
from .verdict import Verdict


class AiJudge(JudgeBackend):
    """A judge that runs a command-line AI; subclasses only implement `run`."""

    def __init__(
        self,
        settings: Settings,
        runner: CommandRunner,
        *,
        clock: Clock,
        work_dir: Path | None = None,
        prompts: JudgePrompts | None = None,
    ) -> None:
        super().__init__(settings, clock=clock, work_dir=work_dir)
        self._runner = runner
        self._prompts = prompts or JudgePrompts()

    @abstractmethod
    def run(self, system: str, prompt: str) -> dict[str, object]:
        """Send the prompts to the tool and return its structured answer. Raises JudgeError."""

    def ask(self, request: JudgeRequest) -> Verdict:
        system = self._prompts.system(request.kind, self.options.max_grant_minutes)
        if self._work_dir is not None:
            self._work_dir.mkdir(parents=True, exist_ok=True)
        try:
            answer = self.run(system, self._prompts.request(request))
            return self._verdict_from(answer, request)
        except JudgeTimeoutError:
            return Verdict(False, speech=t("judge.fallback.timeout"), error="timeout")
        except (JudgeError, ValueError, TypeError) as error:
            return Verdict(False, speech=t("judge.fallback.unreachable", name=t(self.name_key)), error=str(error)[:200])

    def _verdict_from(self, answer: dict[str, object], request: JudgeRequest) -> Verdict:
        """Known groups only, minutes within the limit, bounded speech."""
        verdict = Verdict(
            approved=bool(answer.get("approved")),
            groups=[g for g in answer.get("groups", []) if g in request.context.groups],
            minutes=max(0, min(self.options.max_grant_minutes, int(answer.get("minutes", 0)))),
            speech=str(answer.get("speech", "")).strip()[:240],
        )
        if request.kind is RequestKind.ACCESS and verdict.approved and (not verdict.groups or verdict.minutes <= 0):
            verdict.approved = False
            verdict.speech = verdict.speech or t("judge.fallback.confusing_request")
        return verdict
