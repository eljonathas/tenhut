from __future__ import annotations

from .judge_error import JudgeError


class JudgeTimeoutError(JudgeError):
    """The AI judge did not answer in time."""
