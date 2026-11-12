from __future__ import annotations

import pygame

from tenhut.controllers.active_settings import ActiveSettings
from tenhut.controllers.status_reporter import StatusReporter
from tenhut.core import Clock, Phase, Session
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.painting import ClockText, TextAlign, TextStyle, UiCanvas, UiPalette

from .bar_fill import BarFill
from .cycle_progress import CycleProgress
from .phase_tint import PhaseTint
from .segmented_bar import SegmentedBar
from .status_lines import StatusLines
from .task_area import TaskArea
from .task_list import TaskList
from .tomato_row import TomatoRow


class MissionBoard:
    """What the chalkboard shows during the day: phase, clock, progress, pomodoros, mission, tasks and warnings."""

    TITLE_Y = 12
    TITLE_MARGIN = 8
    CLOCK_Y = 44
    BAR_TOP = 68
    BAR_MARGIN = 14
    BAR_HEIGHT = 8
    COUNT_Y = 82
    RULE_Y = 100
    RULE_MARGIN = 6
    MISSION_Y = 104
    TASKS_Y = 120
    TASKS_RESERVE = 124
    TASK_ROW_HEIGHT = 15
    MIN_TASK_ROWS = 3
    SIDE_MARGIN = 8
    COUNT_MARGIN = 4
    WARNING_SECONDS = 60
    BLINKS_PER_SECOND = 2
    VICTORY_CLOCK = "✓"

    def __init__(
        self, session: Session, settings: ActiveSettings, clock: Clock, *, reporter: StatusReporter, tasks: TaskList
    ) -> None:
        self._session = session
        self._settings = settings
        self._clock = clock
        self._reporter = reporter
        self._tasks = tasks
        self._bar = SegmentedBar()
        self._tomatoes = TomatoRow()
        self._status = StatusLines()

    def draw(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        self._draw_clock(canvas, area)
        self._draw_progress(canvas, area)
        self._draw_mission(canvas, area)

    def _draw_clock(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        session, now, fonts = self._session, self._clock.now(), canvas.fonts
        title = Lettering(fonts.title).fitted(t(session.phase.label_key), area.w - self.TITLE_MARGIN)
        canvas.write(
            title,
            Point(area.centerx, area.y + self.TITLE_Y),
            TextStyle(fonts.title, PhaseTint.label(session.phase), TextAlign.CENTER),
        )
        remaining = self._remaining(now)
        color = UiPalette.CHALK if session.in_mission else UiPalette.CHALK_DIM
        if session.phase is Phase.WORK and remaining < self.WARNING_SECONDS and int(now * self.BLINKS_PER_SECOND) % 2:
            color = UiPalette.YELLOW
        face = ClockText.format(remaining) if session.phase is not Phase.VICTORY else self.VICTORY_CLOCK
        canvas.write(face, Point(area.centerx, area.y + self.CLOCK_Y), TextStyle(fonts.big, color, TextAlign.CENTER))

    def _remaining(self, now: float) -> float:
        if self._session.in_mission:
            return self._session.remaining(now)
        return self._settings.current.timer.work_minutes * ClockText.SECONDS_PER_MINUTE

    def _draw_progress(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        session = self._session
        bar = pygame.Rect(
            area.x + self.BAR_MARGIN, area.y + self.BAR_TOP, area.w - 2 * self.BAR_MARGIN, self.BAR_HEIGHT
        )
        self._bar.draw(canvas, bar, BarFill(session.progress(self._clock.now()), PhaseTint.progress(session.phase)))
        per_cycle = self._settings.current.timer.cycles_before_long_break
        self._tomatoes.draw(
            canvas, Point(area.centerx, area.y), CycleProgress(session.phase, session.cycles, per_cycle)
        )
        count = t("board.pomodoro_count", n=session.cycles)
        canvas.write(
            count,
            Point(area.right - self.COUNT_MARGIN, area.y + self.COUNT_Y),
            TextStyle(canvas.fonts.small, UiPalette.CHALK_DIM, TextAlign.RIGHT),
        )

    def _draw_mission(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        fonts, session = canvas.fonts, self._session
        rule_y = area.y + self.RULE_Y
        canvas.shapes.line(
            UiPalette.CHALK_DIM, (area.x + self.RULE_MARGIN, rule_y), (area.right - self.RULE_MARGIN, rule_y)
        )
        progress = t("board.mission_progress", done=session.done_count(), total=len(session.tasks))
        canvas.write(
            progress, Point(area.x + self.SIDE_MARGIN, area.y + self.MISSION_Y), TextStyle(fonts.body, UiPalette.YELLOW)
        )
        lines = self._reporter.lines()
        rows = max(
            self.MIN_TASK_ROWS,
            (area.h - self.TASKS_RESERVE - len(lines) * StatusLines.LINE_HEIGHT) // self.TASK_ROW_HEIGHT,
        )
        origin = Point(area.x + self.SIDE_MARGIN, area.y + self.TASKS_Y)
        self._tasks.draw(canvas, TaskArea(origin, area.w - 2 * self.SIDE_MARGIN, rows))
        self._status.draw(canvas, area, lines)

    def click(self, position: tuple[int, int]) -> bool:
        return self._tasks.click(position)
