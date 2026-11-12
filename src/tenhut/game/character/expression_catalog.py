from __future__ import annotations

from collections.abc import Iterable

from .angry_expression import AngryExpression
from .expression import Expression
from .happy_expression import HappyExpression
from .mood import Mood
from .neutral_expression import NeutralExpression
from .proud_expression import ProudExpression
from .stern_expression import SternExpression
from .thinking_expression import ThinkingExpression


class ExpressionCatalog:
    """One expression per mood."""

    def __init__(self, expressions: Iterable[Expression]) -> None:
        self._by_mood = {expression.mood: expression for expression in expressions}
        missing = set(Mood) - set(self._by_mood)
        if missing:
            raise ValueError(f"no expression for {sorted(mood.value for mood in missing)}")

    @classmethod
    def standard(cls) -> ExpressionCatalog:
        return cls(
            [
                SternExpression(),
                HappyExpression(),
                AngryExpression(),
                ThinkingExpression(),
                ProudExpression(),
                NeutralExpression(),
            ]
        )

    def for_mood(self, mood: Mood) -> Expression:
        return self._by_mood[mood]
