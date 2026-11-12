from __future__ import annotations

from ...i18n import t
from .group_matcher import GroupMatcher
from .judge_backend import JudgeBackend
from .judge_request import JudgeRequest
from .request_kind import RequestKind
from .verdict import Verdict


class LocalJudge(JudgeBackend):
    """No AI: the general makes the soldier wait (friction) and grants a short pass."""

    name_key = "judge.name.none"
    uses_ai = False
    MAX_PASS_MINUTES = 5

    def available(self) -> bool:
        return True

    def ask(self, request: JudgeRequest) -> Verdict:
        self._clock.sleep(self.options.local_wait_seconds)
        if request.kind is RequestKind.DESERTION:
            return Verdict(True, speech=t("judge.local.desertion_approved"))
        groups = GroupMatcher(self._settings.block_groups).match(request.target)
        if not groups:
            return Verdict(False, speech=t("judge.local.unknown_target", target=request.target))
        minutes = min(self.MAX_PASS_MINUTES, self.options.max_grant_minutes)
        return Verdict(True, groups, minutes, t("judge.local.granted", groups=", ".join(groups), n=minutes))
