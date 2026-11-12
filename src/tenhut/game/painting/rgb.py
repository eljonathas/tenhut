from __future__ import annotations

from typing import NamedTuple


class Rgb(NamedTuple):
    """An opaque colour. A tuple subclass, so pygame accepts it anywhere it takes a colour."""

    red: int
    green: int
    blue: int

    def shaded(self, factor: float) -> Rgb:
        """Every channel multiplied by ``factor`` (below 1 darkens, above 1 lightens), clamped to 0..255."""
        return Rgb(*(max(0, min(255, int(channel * factor))) for channel in self))

    def mixed_with(self, other: Rgb, fraction: float) -> Rgb:
        """The colour ``fraction`` of the way from this one to ``other`` (channels truncated)."""
        return Rgb(*(int(a + (b - a) * fraction) for a, b in zip(self, other)))

    def with_alpha(self, alpha: int) -> tuple[int, int, int, int]:
        return (*self, alpha)

    def brightened(self, amount: int) -> Rgb:
        """Every channel raised by ``amount``, clamped to 255."""
        return Rgb(*(min(255, channel + amount) for channel in self))
