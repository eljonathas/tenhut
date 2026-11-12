from __future__ import annotations

import threading
from collections import deque

from ...core import Clock, HeadPose
from .head_reading import HeadReading


class HeadReadingBuffer:
    """Thread-safe latest reading and recent history, with light smoothing."""

    FRESH_SECONDS = 2.0
    SMOOTHING_SECONDS = 1.0
    HISTORY_SIZE = 80

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._latest: HeadReading | None = None
        self._history: deque[HeadReading] = deque(maxlen=self.HISTORY_SIZE)

    def store(self, pose: HeadPose) -> None:
        """Record a measurement; one close to the previous is averaged with it."""
        now = self._clock.now()
        with self._lock:
            previous = self._latest
            if previous and now - previous.timestamp < self.SMOOTHING_SECONDS:
                pose = HeadPose(0.5 * pose.yaw + 0.5 * previous.pose.yaw, 0.5 * pose.pitch + 0.5 * previous.pose.pitch)
            self._latest = HeadReading(pose, now)
            self._history.append(self._latest)

    def current(self) -> HeadPose | None:
        """The pose of the latest fresh reading, or None when the face is gone."""
        with self._lock:
            latest = self._latest
        fresh = latest is not None and self._clock.now() - latest.timestamp < self.FRESH_SECONDS
        return latest.pose if fresh else None

    def last_seen(self) -> HeadReading | None:
        with self._lock:
            return self._latest

    def seen_since(self, timestamp: float) -> list[HeadReading]:
        with self._lock:
            return [r for r in self._history if r.timestamp >= timestamp]
