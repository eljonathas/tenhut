from __future__ import annotations

from tenhut.services.judge import JudgeJob


class JudgeSlot:
    """Holds the judge job in progress, if any, so everybody can tell the general is waiting for a verdict."""

    def __init__(self) -> None:
        self._job: JudgeJob | None = None

    @property
    def job(self) -> JudgeJob | None:
        return self._job

    @property
    def active(self) -> bool:
        return self._job is not None

    @property
    def waiting_without_ai(self) -> bool:
        return self._job is not None and not self._job.backend.uses_ai

    def occupy(self, job: JudgeJob) -> None:
        self._job = job

    def release(self) -> JudgeJob | None:
        job, self._job = self._job, None
        return job
