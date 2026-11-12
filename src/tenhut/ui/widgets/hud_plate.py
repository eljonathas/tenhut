from __future__ import annotations

import pygame

from tenhut.controllers.active_settings import ActiveSettings
from tenhut.controllers.status_line import StatusLine
from tenhut.controllers.status_reporter import StatusReporter
from tenhut.core import Clock, Phase, Session
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.layout import Layout
from tenhut.ui.painting import ClockText, TextAlign, TextStyle, UiCanvas, UiPalette

from .bar_fill import BarFill
from .flat_bar import FlatBar
from .phase_tint import PhaseTint
from .severity_tint import SeverityTint


class HudPlate:
    """The mini layout's compact plate: phase, clock, progress bar, tasks done and one note."""

    SIZE = (128, 58)
    NOTE_HEIGHT = 12
    TOP_MARGIN = 6
    RIGHT_MARGIN = 134
    PADDING = 6
    PHASE_Y = 7
    LABEL_MARGIN = 4
    CLOCK_Y = 23
    BAR_Y = 34
    BAR_INSET = 4
    BAR_HEIGHT = 4
    PROGRESS_Y = 40
    NOTE_Y = 52
    WARNING_SECONDS = 60
    VICTORY_CLOCK = "OK!"
    MIN_NOTE = 4

    def __init__(self, session: Session, settings: ActiveSettings, clock: Clock, *, reporter: StatusReporter) -> None:
        self._session = session
        self._settings = settings
        self._clock = clock
        self._reporter = reporter
        self._bar = FlatBar()

    def draw(self, canvas: UiCanvas, layout: Layout) -> None:
        notice = self._reporter.hud_notice()
        plate = pygame.Rect(
            layout.size.width - self.RIGHT_MARGIN,
            self.TOP_MARGIN,
            self.SIZE[0],
            self.SIZE[1] + (self.NOTE_HEIGHT if notice else 0),
        )
        shapes = canvas.shapes
        shapes.rect(UiPalette.INK, plate.move(0, 2))
        shapes.rect(UiPalette.INK, plate)
        shapes.rect(UiPalette.WOOD, plate.inflate(-2, -2))
        inner = plate.inflate(-self.PADDING, -self.PADDING)
        shapes.rect(UiPalette.BOARD, inner)
        self._draw_clock(canvas, inner)
        self._draw_progress(canvas, inner)
        if notice:
            self._draw_note(canvas, inner, notice)

    def _draw_clock(self, canvas: UiCanvas, inner: pygame.Rect) -> None:
        session, fonts, now = self._session, canvas.fonts, self._clock.now()
        label = Lettering(fonts.small).fitted(t(session.phase.label_key), inner.w - self.LABEL_MARGIN)
        canvas.write(
            label,
            Point(inner.centerx, inner.y + self.PHASE_Y),
            TextStyle(fonts.small, PhaseTint.label(session.phase), TextAlign.CENTER),
        )
        remaining = (
            session.remaining(now)
            if session.in_mission
            else self._settings.current.timer.work_minutes * ClockText.SECONDS_PER_MINUTE
        )
        blinking = session.phase is Phase.WORK and remaining < self.WARNING_SECONDS and int(now * 2) % 2
        face = ClockText.format(remaining) if session.phase is not Phase.VICTORY else self.VICTORY_CLOCK
        canvas.write(
            face,
            Point(inner.centerx, inner.y + self.CLOCK_Y),
            TextStyle(fonts.mid, UiPalette.YELLOW if blinking else UiPalette.CHALK, TextAlign.CENTER),
        )

    def _draw_progress(self, canvas: UiCanvas, inner: pygame.Rect) -> None:
        session = self._session
        bar = pygame.Rect(inner.x + self.BAR_INSET, inner.y + self.BAR_Y, inner.w - 2 * self.BAR_INSET, self.BAR_HEIGHT)
        self._bar.draw(canvas, bar, BarFill(session.progress(self._clock.now()), PhaseTint.progress(session.phase)))
        text = t("status.hud.mission_progress", done=session.done_count(), total=len(session.tasks))
        canvas.write(
            text,
            Point(inner.x + self.BAR_INSET, inner.y + self.PROGRESS_Y),
            TextStyle(canvas.fonts.small, UiPalette.CHALK_DIM),
        )

    def _draw_note(self, canvas: UiCanvas, inner: pygame.Rect, notice: StatusLine) -> None:
        font, note = canvas.fonts.small, notice.text
        while font.size(note)[0] > inner.w - 2 * self.BAR_INSET and len(note) > self.MIN_NOTE:
            note = note[:-2] + Lettering.ELLIPSIS
        canvas.write(
            note,
            Point(inner.x + self.BAR_INSET, inner.y + self.NOTE_Y),
            TextStyle(font, SeverityTint.of(notice.severity)),
        )
