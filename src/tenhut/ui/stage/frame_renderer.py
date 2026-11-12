from __future__ import annotations

import pygame

from tenhut.controllers.blocking_status import BlockingStatus
from tenhut.controllers.gesture_controller import GestureController
from tenhut.core import Phase, Session
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.layout import Layout, LogicalScreen, Size
from tenhut.ui.pages import PageNavigator
from tenhut.ui.painting import TextStyle, UiCanvas
from tenhut.ui.widgets import Balloon, Chalkboard, HudPlate, RankPlate

from .feedback_overlay import FeedbackOverlay
from .frame_presenter import FramePresenter
from .scene_stage import SceneStage
from .stage_transitions import StageTransitions


class FrameRenderer:
    """Draws one frame: the scene, the plates, the page with its buttons, the balloon and the overlays."""

    RANK_PLATE_X = 6
    RANK_PLATE_LIFT = 30
    DIM_COLOR = (10, 12, 20, 150)
    ERROR_X = 6
    ERROR_LIFT = 44
    ERROR_MAX_LENGTH = 60
    ERROR_COLOR = (255, 220, 220)

    def __init__(
        self,
        *,
        stage: SceneStage,
        transitions: StageTransitions,
        presenter: FramePresenter,
        screen: LogicalScreen,
        navigator: PageNavigator,
        balloon: Balloon,
        gestures: GestureController,
        session: Session,
        blocking: BlockingStatus,
        overlay: FeedbackOverlay,
        rank: RankPlate,
        hud: HudPlate,
    ) -> None:
        self._stage = stage
        self._transitions = transitions
        self._presenter = presenter
        self._screen = screen
        self._navigator = navigator
        self._balloon = balloon
        self._gestures = gestures
        self._session = session
        self._blocking = blocking
        self._overlay = overlay
        self._rank = rank
        self._hud = hud
        self._chalkboard = Chalkboard()
        self._dimmer: pygame.Surface | None = None

    def draw(self) -> None:
        layout, canvas = self._screen.layout, self._screen.canvas
        canvas.surface.blit(self._stage.render(), layout.scene.topleft)
        layout.strategy.paint_ground(canvas, layout.frame, layout.size)
        self._draw_title_card(layout, canvas)
        if not layout.compact:
            self._rank.draw(canvas, Point(self.RANK_PLATE_X, layout.scene.bottom - self.RANK_PLATE_LIFT))
        self._draw_board_or_hud(layout, canvas)
        self._navigator.current.draw_buttons(canvas)
        if self._gestures.poke_animation:
            self._gestures.poke_animation.draw(canvas.surface)
        self._draw_balloon(layout, canvas)
        self._draw_blocking_error(layout, canvas)
        self._overlay.draw(canvas.surface)
        self._presenter.present()

    def _draw_title_card(self, layout: Layout, canvas: UiCanvas) -> None:
        card = self._transitions.title_card
        if card:
            card.place(layout.title_card_placement())
            card.draw(canvas.surface)

    def _draw_board_or_hud(self, layout: Layout, canvas: UiCanvas) -> None:
        if not self._navigator.board_shown:
            self._hud.draw(canvas, layout)
            return
        if layout.compact:
            canvas.surface.blit(self._dim(layout.size), (0, 0))
        self._chalkboard.draw(canvas, layout.board)
        self._navigator.current.draw(canvas, Chalkboard.writing_area(layout.board))

    def _dim(self, size: Size) -> pygame.Surface:
        if self._dimmer is None or self._dimmer.get_size() != tuple(size):
            self._dimmer = pygame.Surface(size, pygame.SRCALPHA)
            self._dimmer.fill(self.DIM_COLOR)
        return self._dimmer

    def _draw_balloon(self, layout: Layout, canvas: UiCanvas) -> None:
        board_shown = self._navigator.board_shown
        if not (layout.compact and board_shown):
            self._balloon.draw(canvas, layout.head, layout.balloon_area(board_shown))

    def _draw_blocking_error(self, layout: Layout, canvas: UiCanvas) -> None:
        error = self._blocking.last_error
        if self._session.phase is Phase.WORK and error:
            message = t("status.blocking.failed", error=error[: self.ERROR_MAX_LENGTH])
            canvas.write(
                message,
                Point(self.ERROR_X, layout.scene.bottom - self.ERROR_LIFT),
                TextStyle(canvas.fonts.small, self.ERROR_COLOR),
            )
