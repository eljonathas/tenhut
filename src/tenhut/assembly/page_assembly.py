from __future__ import annotations

from tenhut.controllers import EditorKind
from tenhut.ui.pages import (
    BoardPage,
    BreakPlan,
    CalibrationPage,
    CalibrationTestPage,
    DesertionPage,
    MainButtonPlan,
    MainPage,
    MissionPage,
    PageContext,
    PageLinks,
    PausedPlan,
    RequestPage,
    SettingsPage,
    StartPlan,
    StepperControl,
    ToggleControl,
    WorkPlan,
)
from tenhut.ui.widgets import CheckMarker, MissionBoard, TaskList, TaskScroll

from .controller_parts import ControllerParts
from .platform_parts import PlatformParts
from .world_parts import WorldParts


class PageAssembly:
    """Creates every page and registers it with the navigator."""

    def __init__(self, platform: PlatformParts, world: WorldParts, controllers: ControllerParts) -> None:
        self._platform = platform
        self._world = world
        self._controllers = controllers

    def assemble(self) -> None:
        navigator = self._controllers.navigator
        context = self._context()
        links, scroll = PageLinks(navigator), TaskScroll()
        board = self._board(scroll)
        for page in (
            MainPage(context, board, self._plans(links), scroll=scroll),
            BoardPage(context, board, scroll, links=links),
            MissionPage(context, self._controllers.mission, scroll, links=links),
            RequestPage(context, self._controllers.judge, links),
            DesertionPage(context, self._controllers.judge, links),
            self._settings_page(context),
            CalibrationPage(context, self._controllers.calibration),
            CalibrationTestPage(context, self._controllers.calibration),
        ):
            navigator.register(page)

    def _context(self) -> PageContext:
        platform, world, controllers = self._platform, self._world, self._controllers
        return PageContext(
            fonts=world.fonts,
            layouts=world.screen,
            session=world.session,
            settings=platform.settings,
            clock=platform.clock,
            navigation=controllers.navigator,
            judge_slot=controllers.judge_slot,
        )

    def _board(self, scroll: TaskScroll) -> MissionBoard:
        platform, world, controllers = self._platform, self._world, self._controllers
        tasks = TaskList(world.session, CheckMarker(), scroll, on_press=controllers.mission.press_task)
        return MissionBoard(
            world.session, platform.settings, platform.clock, reporter=controllers.reporter, tasks=tasks
        )

    def _plans(self, links: PageLinks) -> list[MainButtonPlan]:
        plans = (WorkPlan, BreakPlan, PausedPlan, StartPlan)
        return [plan(self._controllers.mission, self._controllers.judge, links) for plan in plans]

    def _settings_page(self, context: PageContext) -> SettingsPage:
        settings = self._controllers.settings
        controls = {EditorKind.TOGGLE: ToggleControl(settings), EditorKind.STEPPER: StepperControl(settings)}
        return SettingsPage(context, settings, controls)
