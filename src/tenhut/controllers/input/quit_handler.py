from __future__ import annotations

import pygame

from tenhut.controllers.quit_controller import QuitController

from .event_handler import EventHandler


class QuitHandler(EventHandler):
    """The window was closed."""

    def __init__(self, quitting: QuitController) -> None:
        self._quitting = quitting

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.QUIT,)

    def handle(self, event: pygame.event.Event) -> None:
        self._quitting.request_quit()
