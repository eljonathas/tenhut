from __future__ import annotations

import pygame

from tenhut.controllers.feedback_controller import FeedbackController
from tenhut.game.random_source import RandomSource
from tenhut.ui.layout import LogicalScreen
from tenhut.ui.painting import UiPalette

from .display_window import DisplayWindow


class FramePresenter:
    """Scales the logical screen onto the window, shaking it when the general bangs the desk."""

    SHAKE_STEPS = (-2, -1, 1, 2)

    def __init__(
        self, window: DisplayWindow, screen: LogicalScreen, feedback: FeedbackController, *, randomness: RandomSource
    ) -> None:
        self._window = window
        self._screen = screen
        self._feedback = feedback
        self._randomness = randomness

    def present(self) -> None:
        scale = self._screen.scale
        offset_x, offset_y = self._screen.offset
        if self._feedback.screen_shaking:
            offset_x += self._randomness.choice(self.SHAKE_STEPS) * scale
            offset_y += self._randomness.choice(self.SHAKE_STEPS) * scale
        window = self._window.surface
        surface = self._screen.surface
        if scale == 1 and (offset_x, offset_y) == (0, 0):
            window.blit(surface, (0, 0))
        else:
            window.fill(UiPalette.LETTERBOX)
            window.blit(pygame.transform.scale_by(surface, scale) if scale > 1 else surface, (offset_x, offset_y))
        pygame.display.flip()
