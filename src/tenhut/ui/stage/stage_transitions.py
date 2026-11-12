from __future__ import annotations

import pygame

from tenhut.core import Clock, Phase, Session, Theme
from tenhut.game.animations import CurtainTransition, TitleCard, TitleCardContent, TitleCardFonts
from tenhut.i18n import t
from tenhut.ui.fonts import FontSet
from tenhut.ui.layout import LayoutProvider

from .stage_listener import StageListener


class StageTransitions:
    """The curtain that falls when the scenery changes and the title card that announces a new stage."""

    def __init__(
        self, session: Session, fonts: FontSet, clock: Clock, *, layouts: LayoutProvider, listener: StageListener
    ) -> None:
        self._session = session
        self._fonts = fonts
        self._clock = clock
        self._layouts = layouts
        self._listener = listener
        self._theme: Theme | None = None
        self._curtain: CurtainTransition | None = None
        self._title_card: TitleCard | None = None

    @property
    def title_card(self) -> TitleCard | None:
        """The title card on screen, if it has not run out yet."""
        if self._title_card is not None and self._title_card.finished:
            self._title_card = None
        return self._title_card

    def observe(self, theme: Theme, scene: pygame.Surface) -> None:
        """Starts the transition when ``theme`` is not the one that was on screen; ``scene`` is what the curtain hides."""
        previous, self._theme = self._theme, theme
        if previous is None or previous == theme:
            return
        self._curtain = CurtainTransition(scene.copy())
        if theme.stage_number > previous.stage_number or self._session.phase is Phase.VICTORY:
            self._announce(theme)

    def cancel_curtain(self) -> None:
        self._curtain = None

    def update(self, dt: float) -> None:
        if self._curtain:
            self._curtain.update(dt)
            if self._curtain.finished:
                self._curtain = None

    def draw_curtain(self, scene: pygame.Surface) -> None:
        if self._curtain:
            self._curtain.draw(scene)

    def _announce(self, theme: Theme) -> None:
        session = self._session
        content = TitleCardContent(
            t("theme.title_card.stage", n=theme.stage_number, title=t(theme.title_key)),
            t("theme.title_card.tasks_progress", done=session.done_count(), total=len(session.tasks)),
        )
        fonts = TitleCardFonts(self._fonts.title, self._fonts.small)
        self._title_card = TitleCard(content, fonts, self._clock, placement=self._layouts.layout.title_card_placement())
        self._listener.stage_entered(theme)
