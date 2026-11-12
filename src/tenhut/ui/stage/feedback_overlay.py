from __future__ import annotations

import pygame

from tenhut.controllers.feedback_controller import FeedbackController
from tenhut.controllers.navigation import Navigation
from tenhut.game.geometry import Point
from tenhut.ui.layout import LayoutProvider


class FeedbackOverlay:
    """Draws the floating texts, the rubber stamp and the red flash over everything else."""

    POPUP_OFFSET_X = 30
    FLASH_COLOR = (220, 30, 30)
    FLASH_MAX_ALPHA = 110
    FLASH_GAIN = 2.5

    def __init__(self, feedback: FeedbackController, layouts: LayoutProvider, navigation: Navigation) -> None:
        self._feedback = feedback
        self._layouts = layouts
        self._navigation = navigation

    def draw(self, screen: pygame.Surface) -> None:
        layout = self._layouts.layout
        head = layout.head
        self._feedback.popups.anchor_at(Point(head.x + self.POPUP_OFFSET_X, head.y))
        self._feedback.popups.draw(screen)
        stamp = self._feedback.stamp
        if stamp:
            stamp.place(layout.stamp_placement(self._navigation.board_shown))
            stamp.draw(screen)
        level = self._feedback.flash_level
        if level > 0:
            wash = pygame.Surface(layout.size, pygame.SRCALPHA)
            wash.fill((*self.FLASH_COLOR, int(self.FLASH_MAX_ALPHA * min(1.0, level * self.FLASH_GAIN))))
            screen.blit(wash, (0, 0))
