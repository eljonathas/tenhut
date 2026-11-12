from __future__ import annotations

from tenhut.game.geometry import Point

from .size import Size


class WindowScaler:
    """Integer pixel scaling: the logical screen is drawn N times bigger and centred in the window."""

    MIN_WINDOW = Size(320, 240)
    WIDE_BASE = Size(480, 300)
    TALL_BASE = Size(300, 460)

    def __init__(self, min_window: Size = MIN_WINDOW) -> None:
        self._min_logical = Size(min_window.width // 2, min_window.height // 2)
        self._scale = 1
        self._offset = Point(0, 0)
        self._logical = Size(0, 0)

    @property
    def scale(self) -> int:
        return self._scale

    @property
    def offset(self) -> Point:
        return self._offset

    @property
    def logical_size(self) -> Size:
        return self._logical

    @classmethod
    def scale_for(cls, window: Size) -> int:
        """The largest integer scale that still leaves room for a lying or a standing layout."""
        lying = min(window.width // cls.WIDE_BASE.width, window.height // cls.WIDE_BASE.height)
        standing = min(window.width // cls.TALL_BASE.width, window.height // cls.TALL_BASE.height)
        return max(1, lying, standing)

    def logical_for(self, window: Size) -> Size:
        scale = self.scale_for(window)
        return Size(
            max(self._min_logical.width, window.width // scale), max(self._min_logical.height, window.height // scale)
        )

    def resize(self, window: Size, *, force: bool = False) -> bool:
        """Adopts a new window size; False when the logical size and scale did not change (and ``force`` is off)."""
        scale = self.scale_for(window)
        logical = self.logical_for(window)
        if not force and (logical, scale) == (self._logical, self._scale):
            return False
        self._scale = scale
        self._logical = logical
        self._offset = Point((window.width - logical.width * scale) // 2, (window.height - logical.height * scale) // 2)
        return True

    def to_logical(self, position: tuple[int, int]) -> tuple[int, int]:
        return (position[0] - int(self._offset.x)) // self._scale, (position[1] - int(self._offset.y)) // self._scale
