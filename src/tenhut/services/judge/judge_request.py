from __future__ import annotations

from dataclasses import dataclass

from .judge_context import JudgeContext
from .request_kind import RequestKind


@dataclass(frozen=True, slots=True)
class JudgeRequest:
    """What the soldier asks for, and why."""

    kind: RequestKind
    target: str
    justification: str
    context: JudgeContext
