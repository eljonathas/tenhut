from __future__ import annotations

from .character_state import CharacterState
from .happy_expression import HappyExpression
from .mood import Mood


class ProudExpression(HappyExpression):
    """As happy, but his eyes stay closed in satisfaction for as long as he is quiet."""

    @property
    def mood(self) -> Mood:
        return Mood.PROUD

    def has_content_eyes(self, state: CharacterState) -> bool:
        return not state.talking
