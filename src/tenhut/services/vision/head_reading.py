from __future__ import annotations

from dataclasses import dataclass

from ...core import HeadPose


@dataclass(frozen=True, slots=True)
class HeadReading:
    """A head pose and the moment it was measured."""

    pose: HeadPose
    timestamp: float
