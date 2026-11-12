import pygame

from tenhut.controllers import ActivePage, RunState
from tenhut.controllers.input import FocusHandler, InputRouter, KeyHandler, VisibilityHandler, WheelHandler


class FakePage(ActivePage):
    def __init__(self, space_used=False):
        self.events, self.calls, self.space_used = [], [], space_used

    def handle_widget_event(self, event):
        self.events.append(event.type)
        return False

    def click_board(self, position):
        self.calls.append(("click", position))

    def scroll(self, rows):
        self.calls.append(("scroll", rows))

    def escape(self):
        self.calls.append("escape")

    def press_space(self):
        self.calls.append("space")
        return self.space_used

    def cycle_focus(self):
        self.calls.append("tab")


def key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


def test_escape_and_tab_are_page_shortcuts_and_do_not_reach_the_fields():
    page = FakePage()
    router = InputRouter([KeyHandler(page)])
    router.dispatch(key(pygame.K_ESCAPE))
    router.dispatch(key(pygame.K_TAB))
    assert page.calls == ["escape", "tab"] and page.events == []


def test_space_goes_to_the_fields_unless_the_page_uses_it():
    unused, used = FakePage(False), FakePage(True)
    InputRouter([KeyHandler(unused)]).dispatch(key(pygame.K_SPACE))
    InputRouter([KeyHandler(used)]).dispatch(key(pygame.K_SPACE))
    assert unused.events == [pygame.KEYDOWN] and used.events == []


def test_other_keys_go_to_the_fields():
    page = FakePage()
    InputRouter([KeyHandler(page)]).dispatch(key(pygame.K_a))
    assert page.events == [pygame.KEYDOWN]


def test_the_wheel_scrolls_the_page():
    page = FakePage()
    InputRouter([WheelHandler(page)]).dispatch(pygame.event.Event(pygame.MOUSEWHEEL, y=-2))
    assert page.calls == [("scroll", -2)]


def test_events_without_a_handler_are_ignored():
    InputRouter([]).dispatch(key(pygame.K_a))


def test_focus_and_visibility_update_the_run_state():
    state = RunState()
    router = InputRouter([FocusHandler(state), VisibilityHandler.hiding(state), VisibilityHandler.showing(state)])
    router.dispatch(pygame.event.Event(pygame.WINDOWFOCUSLOST))
    assert not state.focused
    router.dispatch(pygame.event.Event(pygame.WINDOWFOCUSGAINED))
    assert state.focused
    router.dispatch(pygame.event.Event(pygame.WINDOWMINIMIZED))
    assert state.hidden
    router.dispatch(pygame.event.Event(pygame.WINDOWRESTORED))
    assert not state.hidden
