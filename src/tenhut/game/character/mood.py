from __future__ import annotations

from enum import Enum


class Mood(Enum):
    """How the general feels; picks his face."""

    STERN = "stern"
    HAPPY = "happy"
    ANGRY = "angry"
    THINKING = "thinking"
    PROUD = "proud"
    NEUTRAL = "neutral"
