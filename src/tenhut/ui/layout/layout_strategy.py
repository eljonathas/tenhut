from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

import pygame

from tenhut.ui.painting import UiCanvas

from .layout_frame import LayoutFrame
from .layout_mode import LayoutMode
from .size import Size


class LayoutStrategy(ABC):
    """One way of arranging the screen; subclasses decide which window shapes they fit and where things go."""

    BUTTON_HEIGHT: ClassVar[int] = 24
    TOP_MARGIN: ClassVar[int] = 4
    SIDE_MARGIN: ClassVar[int] = 6
    DEFAULT_SCENE_DOUBLING_HEIGHT: ClassVar[int] = 300
    compact: ClassVar[bool] = False

    @property
    @abstractmethod
    def mode(self) -> LayoutMode: ...

    @property
    def doubling_height(self) -> int:
        """The scene height from which the world is drawn at double size."""
        return self.DEFAULT_SCENE_DOUBLING_HEIGHT

    @abstractmethod
    def accepts(self, size: Size) -> bool: ...

    @abstractmethod
    def frame(self, size: Size) -> LayoutFrame: ...

    @abstractmethod
    def balloon_area(self, frame: LayoutFrame, size: Size, board_shown: bool) -> pygame.Rect:
        """Where the speech balloon may be drawn."""

    def title_region(self, frame: LayoutFrame) -> pygame.Rect:
        """The part of the screen the stage title card is centred in."""
        return frame.scene

    def paint_ground(self, canvas: UiCanvas, frame: LayoutFrame, size: Size) -> None:
        """Paints what lies below the scene when the scene does not fill the window."""
        return None
