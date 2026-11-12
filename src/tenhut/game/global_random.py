from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


class GlobalRandom:
    """Delegates to the module-level ``random`` stream, so ``random.seed`` still drives the whole game."""

    def random(self) -> float:
        return random.random()

    def uniform(self, low: float, high: float) -> float:
        return random.uniform(low, high)

    def randint(self, low: int, high: int) -> int:
        return random.randint(low, high)

    def randrange(self, start: int, stop: int) -> int:
        return random.randrange(start, stop)

    def choice(self, options: Sequence[T]) -> T:
        return random.choice(options)
