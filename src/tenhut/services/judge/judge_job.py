from __future__ import annotations

import threading

from ...core import Clock
from .judge_backend import JudgeBackend
from .judge_request import JudgeRequest
from .verdict import Verdict


class JudgeJob(threading.Thread):
    """Asks `backend` about `request` on a daemon thread; the answer lands in `result`."""

    def __init__(self, backend: JudgeBackend, request: JudgeRequest, clock: Clock) -> None:
        super().__init__(daemon=True, name="judge")
        self.backend = backend
        self.request = request
        self.started_at = clock.now()
        self.result: Verdict | None = None

    def run(self) -> None:
        self.result = self.backend.ask(self.request)
