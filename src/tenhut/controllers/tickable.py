from __future__ import annotations

from abc import ABC, abstractmethod


class Tickable(ABC):
    """Something that advances once per frame, before drawing."""

    @abstractmethod
    def tick(self, dt: float) -> None: ...
