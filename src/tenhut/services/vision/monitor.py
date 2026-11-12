from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Monitor:
    """A screen and its place on the virtual desktop, in pixels."""

    name: str
    x: int
    y: int
    width: int
    height: int
    primary: bool

    @property
    def right(self) -> int:
        return self.x + self.width
