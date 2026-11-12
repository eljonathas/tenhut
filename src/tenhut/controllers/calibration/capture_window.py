from __future__ import annotations

import math

from tenhut.core import HeadPose


class CaptureWindow:
    """A capture in progress: a countdown, then two seconds of head poses collected."""

    COUNTDOWN_SECONDS = 3.0
    SAMPLING_SECONDS = 2.0
    FIRST_BEEP = 4

    def __init__(self) -> None:
        self._count_until = 0.0
        self._sampling_until = 0.0
        self._samples: list[HeadPose] | None = None
        self._started_at = 0.0
        self._beep = 0

    @property
    def counting_down(self) -> bool:
        return bool(self._count_until)

    @property
    def sampling(self) -> bool:
        return self._samples is not None

    @property
    def busy(self) -> bool:
        return self.sampling or self.counting_down

    @property
    def started_at(self) -> float:
        return self._started_at

    def seconds_left(self, now: float) -> int:
        return max(1, math.ceil(self._count_until - now))

    def progress(self, now: float) -> float:
        return 1 - max(0.0, self._sampling_until - now) / self.SAMPLING_SECONDS

    def start(self, now: float) -> None:
        self._count_until = now + self.COUNTDOWN_SECONDS
        self._started_at = now
        self._beep = self.FIRST_BEEP

    def cancel(self) -> None:
        self._samples = None
        self._count_until = 0.0

    def beep_due(self, now: float) -> bool:
        """True once per second of the countdown."""
        left = math.ceil(self._count_until - now)
        if left != self._beep and left > 0:
            self._beep = left
            return True
        return False

    def countdown_over(self, now: float) -> bool:
        return now >= self._count_until

    def begin_sampling(self, now: float) -> None:
        self._count_until = 0.0
        self._samples = []
        self._sampling_until = now + self.SAMPLING_SECONDS

    def add(self, pose: HeadPose | None) -> None:
        if pose and self._samples is not None:
            self._samples.append(pose)

    def sampling_over(self, now: float) -> bool:
        return now >= self._sampling_until

    def take_samples(self) -> list[HeadPose]:
        samples, self._samples = self._samples or [], None
        return samples
