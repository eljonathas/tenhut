from __future__ import annotations

import pygame

from tenhut.controllers.active_page import ActivePage
from tenhut.controllers.navigation import Navigation
from tenhut.ui.layout import LayoutProvider
from tenhut.ui.widgets.balloon import Balloon

from .event_handler import EventHandler
from .pointer_translator import PointerTranslator
from .poke_back_responder import PokeBackResponder


class MousePressHandler(EventHandler):
    """A mouse button went down: fields take focus; otherwise a click on the board, or on the general."""

    def __init__(
        self,
        page: ActivePage,
        translator: PointerTranslator,
        layouts: LayoutProvider,
        *,
        navigation: Navigation,
        balloon: Balloon,
        poke_back: PokeBackResponder,
    ) -> None:
        self._page = page
        self._translator = translator
        self._layouts = layouts
        self._navigation = navigation
        self._balloon = balloon
        self._poke_back = poke_back

    @property
    def event_types(self) -> tuple[int, ...]:
        return (pygame.MOUSEBUTTONDOWN,)

    def handle(self, event: pygame.event.Event) -> None:
        event = self._translator.translate(event)
        if self._page.handle_widget_event(event) or event.button != pygame.BUTTON_LEFT:
            return
        on_board = self._navigation.board_shown and self._layouts.layout.board.collidepoint(event.pos)
        if on_board:
            self._page.click_board(event.pos)
            return
        if not self._poke_back.respond(event.pos):
            self._balloon.skip()
            self._page.click_board(event.pos)
