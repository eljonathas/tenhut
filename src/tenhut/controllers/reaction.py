from __future__ import annotations

from enum import Enum

from tenhut.game.character import Mood, PoseName


class Reaction(Enum):
    """The mood and pose the general takes while saying something."""

    STERN_POINT = (Mood.STERN, PoseName.POINT)
    STERN_CROSSED = (Mood.STERN, PoseName.CROSSED)
    ANGRY_POINT = (Mood.ANGRY, PoseName.POINT)
    ANGRY_FISTS_UP = (Mood.ANGRY, PoseName.FISTS_UP)
    NEUTRAL_POINT = (Mood.NEUTRAL, PoseName.POINT)
    NEUTRAL_SALUTE = (Mood.NEUTRAL, PoseName.SALUTE)
    NEUTRAL_BEHIND = (Mood.NEUTRAL, PoseName.BEHIND)
    HAPPY_THUMBS = (Mood.HAPPY, PoseName.THUMBS)
    HAPPY_COFFEE = (Mood.HAPPY, PoseName.COFFEE)
    PROUD_THUMBS = (Mood.PROUD, PoseName.THUMBS)
    PROUD_SALUTE = (Mood.PROUD, PoseName.SALUTE)
    THINKING_CHIN = (Mood.THINKING, PoseName.CHIN)

    @property
    def mood(self) -> Mood:
        return self.value[0]

    @property
    def pose(self) -> PoseName:
        return self.value[1]
