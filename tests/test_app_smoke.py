"""Headless smoke tests: every page renders, at every layout, in both languages, without raising."""

import pygame
import pytest

from tenhut import i18n
from tenhut.application import Application
from tenhut.application_options import ApplicationOptions
from tenhut.controllers import PageId
from tenhut.core import HeadPose, Phase, Theme


@pytest.fixture
def app():
    application = Application(ApplicationOptions(dry_run=True, headless=True))
    yield application
    pygame.quit()


def run(app, frames=3):
    for _ in range(frames):
        for event in pygame.event.get():
            app.handle(event)
        app.tick(1 / 30)
        app.draw()


def resize(app, size):
    pygame.display.set_mode(size)
    app.resize()


def add_tasks(app, *texts):
    controllers = app.parts.controllers
    controllers.mission.new_mission()
    for text in texts:
        page = controllers.navigator.current
        page.inputs[0].text = text
        page.add_task()


@pytest.mark.parametrize("lang", ["pt", "en"])
@pytest.mark.parametrize("size", [(1120, 720), (600, 1000), (360, 260)])
def test_every_page_renders(app, lang, size):
    i18n.set_language(lang)
    resize(app, size)
    navigator = app.parts.controllers.navigator
    recorder = app.parts.controllers.calibration._recorder
    recorder.record_base(HeadPose(0, 0))
    recorder.record_down(HeadPose(0, 20))
    for page_id in PageId:
        navigator.open(page_id)
        run(app)
    app.parts.controllers.calibration.cancel()
    navigator.open(PageId.MAIN)
    add_tasks(app, "write the tests")
    app.parts.controllers.mission.start_mission()
    run(app, 10)
    assert app.parts.world.session.in_mission


def test_mission_flow_reaches_every_scene(app):
    add_tasks(app, "a", "b", "c", "d")
    mission = app.parts.controllers.mission
    mission.start_mission()
    seen = set()
    for index in range(4):
        run(app, 40)
        seen.add(app.parts.stage._transitions._theme)
        mission.toggle_task(index)
    run(app, 40)
    assert set(Theme) <= seen | {app.parts.stage._transitions._theme}
    assert app.parts.world.session.phase is Phase.VICTORY


def test_desertion_offers_resume_or_new_mission(app):
    add_tasks(app, "a", "b")
    controllers, session = app.parts.controllers, app.parts.world.session
    controllers.mission.start_mission()
    controllers.mission.toggle_task(0)
    session.end_mission(False)
    controllers.navigator.open(PageId.MAIN)
    labels = [button.label for button in controllers.navigator.current.buttons]
    assert "CONTINUAR" in labels
    next(button for button in controllers.navigator.current.buttons if button.label == "CONTINUAR").action()
    assert session.phase is Phase.WORK and session.tasks[0].done


def test_new_mission_asks_for_confirmation_before_discarding(app):
    add_tasks(app, "keep me")
    controllers, session = app.parts.controllers, app.parts.world.session
    session.end_mission(False)
    controllers.navigator.open(PageId.MAIN)
    controllers.mission.fresh_mission()
    assert session.tasks
    controllers.mission.fresh_mission()
    assert session.tasks == ()


def test_the_confirmation_button_turns_red_and_asks_again(app):
    add_tasks(app, "keep me")
    controllers = app.parts.controllers
    app.parts.world.session.end_mission(False)
    controllers.navigator.open(PageId.MAIN)
    controllers.mission.fresh_mission()
    labels = [button.label for button in controllers.navigator.current.buttons]
    assert i18n.t("button.confirm") in labels


def test_volume_is_adjustable_while_working_but_timers_are_not(app):
    add_tasks(app, "x")
    controllers = app.parts.controllers
    controllers.mission.start_mission()
    controllers.navigator.open(PageId.SETTINGS)
    settings = controllers.settings
    from tenhut.controllers.settings import SettingKey

    row = lambda key: next(r for r in settings.rows() if r.key is key)  # noqa: E731
    volume = app.parts.platform.settings.current.sound.volume
    settings.click(row(SettingKey.VOLUME), -1)
    assert settings.value(SettingKey.VOLUME) == volume - 10
    before = settings.value(SettingKey.WORK_MINUTES)
    settings.click(row(SettingKey.WORK_MINUTES), 1)
    assert settings.value(SettingKey.WORK_MINUTES) == before


def test_the_window_is_minimised_instead_of_closed_during_a_combat(app):
    add_tasks(app, "x")
    app.parts.controllers.mission.start_mission()
    app.handle(pygame.event.Event(pygame.QUIT))
    assert app.parts.controllers.run_state.running
    app.parts.world.session.end_mission(False)
    app.handle(pygame.event.Event(pygame.QUIT))
    assert not app.parts.controllers.run_state.running


def test_resizing_rebuilds_the_page_keeping_what_was_typed(app):
    add_tasks(app)
    navigator = app.parts.controllers.navigator
    navigator.current.inputs[0].text = "half a task"
    resize(app, (600, 1000))
    assert navigator.current.inputs[0].text == "half a task"


def test_the_board_page_gives_way_to_the_main_page_when_the_layout_grows(app):
    resize(app, (360, 260))
    navigator = app.parts.controllers.navigator
    navigator.open(PageId.BOARD)
    resize(app, (1120, 720))
    assert navigator.current_id is PageId.MAIN


def test_the_fps_policy_follows_focus_and_visibility(app):
    from tenhut.controllers import FpsPolicy

    state = app.parts.controllers.run_state
    assert FpsPolicy.frames_per_second(state) == 30
    state.focus(False)
    assert FpsPolicy.frames_per_second(state) == 12
    state.hide(True)
    assert FpsPolicy.frames_per_second(state) == 2
