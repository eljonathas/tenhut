from __future__ import annotations

import pygame

from tenhut.controllers.active_page import ActivePage

from .event_handler import EventHandler


class KeyHandler(EventHandler):
    """A key went down: Escape, Space and Tab have page-level meanings; the rest goes to the fields."""

    def __init__(self, page: ActivePage) -> None:
        self._page = page
        self._shortcuts = {
            pygame.K_ESCAPE: self._escape,
            pygame.K_SPACE: self._page.press_space,
            pygame.K_TAB: self._tab,
        }

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.KEYDOWN,)

    def handle(self, event: pygame.event.Event) -> None:
        shortcut = self._shortcuts.get(event.key)
        if shortcut is None or not shortcut():
            self._page.handle_widget_event(event)

    def _escape(self) -> bool:
        self._page.escape()
        return True

    def _tab(self) -> bool:
        self._page.cycle_focus()
        return True
