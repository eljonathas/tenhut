from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TypeVar

T = TypeVar("T")


class RandomSource(Protocol):
    """The slice of ``random`` the game uses; ``random.Random`` instances satisfy it as they are."""

    def random(self) -> float: ...

    def uniform(self, low: float, high: float) -> float: ...

    def randint(self, low: int, high: int) -> int: ...

    def randrange(self, start: int, stop: int) -> int: ...

    def choice(self, options: Sequence[T]) -> T: ...
