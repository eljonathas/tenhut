import pygame
import pytest

from tenhut import i18n
from tenhut.application import Application
from tenhut.application_options import ApplicationOptions
from tenhut.controllers import PageId, Severity, StatusLine
from tenhut.core import Phase
from tenhut.services.judge import RequestKind
from tenhut.ui.pages import BreakPlan, PausedPlan, StartPlan, WorkPlan


@pytest.fixture
def app():
    application = Application(ApplicationOptions(dry_run=True, headless=True))
    yield application
    pygame.quit()


def labels(app):
    return [button.label for button in app.parts.controllers.navigator.current.buttons]


def start_mission(app, *tasks):
    mission = app.parts.controllers.mission
    mission.new_mission()
    for task in tasks:
        page = app.parts.controllers.navigator.current
        page.inputs[0].text = task
        page.add_task()
    mission.start_mission()


class LiveJob:
    """A judge job that never finishes."""

    class backend:
        uses_ai = True

    def is_alive(self):
        return True


class TestMainPageButtons:
    def test_the_idle_page_offers_a_new_mission_and_the_settings(self, app):
        assert labels(app) == [i18n.t("button.new_mission"), i18n.t("button.settings")]

    def test_during_work_it_offers_a_pass_tasks_and_desertion(self, app):
        start_mission(app, "a")
        assert labels(app) == [i18n.t("button.request_pass"), i18n.t("button.add_task"), i18n.t("button.desert")]

    def test_during_a_break_it_offers_to_go_back_to_work(self, app):
        start_mission(app, "a")
        session = app.parts.world.session
        session.expire_phase(0)
        session.tick(app.parts.platform.settings.current, 1.0)
        app.parts.controllers.navigator.open(PageId.MAIN)
        assert session.phase is Phase.SHORT and i18n.t("button.back_to_work") in labels(app)

    def test_each_plan_knows_when_it_applies(self, app):
        mission, judge = app.parts.controllers.mission, app.parts.controllers.judge
        from tenhut.ui.pages import PageLinks

        links = PageLinks(app.parts.controllers.navigator)
        plans = [plan(mission, judge, links) for plan in (WorkPlan, BreakPlan, PausedPlan, StartPlan)]
        chosen = {phase: next(p for p in plans if p.applies(phase, 0)).__class__ for phase in Phase}
        assert chosen[Phase.WORK] is WorkPlan and chosen[Phase.SHORT] is BreakPlan
        assert chosen[Phase.LONG] is BreakPlan and chosen[Phase.IDLE] is StartPlan
        assert next(p for p in plans if p.applies(Phase.IDLE, 2)).__class__ is PausedPlan

    def test_a_compact_layout_uses_shorter_labels_and_a_board_button(self, app):
        pygame.display.set_mode((360, 260))
        app.resize()
        assert i18n.t("button.mission_short") in labels(app) and i18n.t("button.board") in labels(app)


class TestPageNavigator:
    def test_open_makes_the_page_current_and_builds_it(self, app):
        navigator = app.parts.controllers.navigator
        navigator.open(PageId.MISSION)
        assert navigator.current_id is PageId.MISSION and navigator.current.inputs and navigator.current.buttons

    def test_refresh_only_rebuilds_the_page_that_is_open(self, app):
        navigator = app.parts.controllers.navigator
        navigator.open(PageId.MISSION)
        buttons = navigator.current.buttons
        navigator.refresh(PageId.MAIN)
        assert navigator.current.buttons is buttons
        navigator.refresh(PageId.MISSION)
        assert navigator.current.buttons is not buttons

    def test_the_board_is_always_shown_on_a_big_layout_and_on_request_in_the_mini_one(self, app):
        navigator = app.parts.controllers.navigator
        assert navigator.board_shown
        pygame.display.set_mode((360, 260))
        app.resize()
        assert not navigator.board_shown
        navigator.open(PageId.BOARD)
        assert navigator.board_shown

    def test_escape_returns_to_the_main_page_except_while_the_judge_thinks(self, app):
        navigator = app.parts.controllers.navigator
        navigator.open(PageId.SETTINGS)
        navigator.escape()
        assert navigator.current_id is PageId.MAIN
        navigator.open(PageId.REQUEST)
        app.parts.controllers.judge_slot.occupy(LiveJob())
        navigator.escape()
        assert navigator.current_id is PageId.REQUEST

    def test_tab_cycles_the_focus_between_fields(self, app):
        navigator = app.parts.controllers.navigator
        navigator.open(PageId.REQUEST)
        first, second = navigator.current.inputs
        assert first.focused and not second.focused
        navigator.cycle_focus()
        assert second.focused and not first.focused
        navigator.cycle_focus()
        assert first.focused

    def test_a_page_without_text_fields_ignores_tab(self, app):
        app.parts.controllers.navigator.cycle_focus()


class TestMissionPage:
    def test_the_start_button_waits_for_a_task(self, app):
        controllers = app.parts.controllers
        controllers.mission.new_mission()
        page = controllers.navigator.current
        start = next(b for b in page.buttons if b.label == i18n.t("button.start_mission"))
        assert not start.enabled
        page.inputs[0].text = "first"
        page.add_task()
        assert start.enabled and page.inputs[0].text == ""

    def test_an_empty_task_is_not_added(self, app):
        controllers = app.parts.controllers
        controllers.mission.new_mission()
        controllers.navigator.current.add_task()
        assert app.parts.world.session.tasks == ()

    def test_clicking_a_task_removes_it_before_the_mission(self, app):
        controllers = app.parts.controllers
        controllers.mission.new_mission()
        page = controllers.navigator.current
        page.inputs[0].text = "first"
        page.add_task()
        app.draw()
        page.click_board(page._tasks._rows[0].rect.center)
        assert app.parts.world.session.tasks == ()


class TestRequestPages:
    def test_the_request_page_has_a_target_and_a_justification_field(self, app):
        navigator = app.parts.controllers.navigator
        navigator.open(PageId.REQUEST)
        assert len(navigator.current.inputs) == 2 and navigator.current.kind is RequestKind.ACCESS

    def test_the_desertion_page_has_only_the_justification_field_and_it_is_focused(self, app):
        navigator = app.parts.controllers.navigator
        navigator.open(PageId.DESERTION)
        assert len(navigator.current.inputs) == 1 and navigator.current.inputs[0].focused
        assert navigator.current.kind is RequestKind.DESERTION

    def test_the_buttons_lock_while_the_judge_thinks(self, app):
        navigator = app.parts.controllers.navigator
        navigator.open(PageId.REQUEST)
        app.parts.controllers.judge_slot.occupy(LiveJob())
        app.tick(0.03)
        assert not any(button.enabled for button in navigator.current.buttons)

    def test_a_resize_keeps_the_typed_justification_and_the_lock(self, app):
        navigator = app.parts.controllers.navigator
        navigator.open(PageId.REQUEST)
        navigator.current.inputs[1].text = "because"
        app.parts.controllers.judge_slot.occupy(LiveJob())
        pygame.display.set_mode((600, 1000))
        app.resize()
        assert navigator.current.inputs[1].text == "because"
        assert not any(button.enabled for button in navigator.current.buttons)


class TestSettingsPage:
    def test_opening_it_starts_a_fresh_draft_and_closing_it_goes_back(self, app):
        controllers = app.parts.controllers
        controllers.navigator.open(PageId.SETTINGS)
        app.draw()
        next(b for b in controllers.navigator.current.buttons if b.label == i18n.t("button.back")).action()
        assert controllers.navigator.current_id is PageId.MAIN

    def test_clicking_a_stepper_changes_the_draft(self, app):
        from tenhut.controllers import SettingKey

        controllers = app.parts.controllers
        controllers.navigator.open(PageId.SETTINGS)
        app.draw()
        page = controllers.navigator.current
        before = controllers.settings.value(SettingKey.WORK_MINUTES)
        row_y = page._targets[2].rect.centery
        plus = next(t for t in page._targets if t.rect.centery == row_y and t.rect.x > page._targets[2].rect.x)
        page.click_board(plus.rect.center)
        assert controllers.settings.value(SettingKey.WORK_MINUTES) == before + 5


class TestStatusReporter:
    def test_a_paused_mission_is_reported(self, app):
        start_mission(app, "a", "b")
        app.parts.world.session.end_mission(False)
        lines = app.parts.controllers.reporter.lines()
        assert lines[0].severity is Severity.NOTICE

    def test_an_active_pass_is_reported_in_green_and_in_the_hud(self, app):
        start_mission(app, "a")
        session = app.parts.world.session
        session.grant("YouTube", app.parts.platform.clock.now() + 300)
        reporter = app.parts.controllers.reporter
        assert any(line.severity is Severity.SUCCESS and "YouTube" in line.text for line in reporter.lines())
        assert reporter.hud_notice() == StatusLine(reporter.hud_notice().text, Severity.SUCCESS)

    def test_at_most_four_lines(self, app):
        start_mission(app, "a")
        assert len(app.parts.controllers.reporter.lines()) <= 4

    def test_no_notice_when_nothing_to_say(self, app):
        assert app.parts.controllers.reporter.hud_notice() is None
