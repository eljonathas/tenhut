import pygame
import pytest

from tenhut.core import Phase
from tenhut.game.audio import SoundBank
from tenhut.game.geometry import Point
from tenhut.ui.fonts import FontSet
from tenhut.ui.painting import ClockText, TextWrapper, UiCanvas
from tenhut.ui.widgets import (
    Balloon,
    Button,
    ButtonRow,
    ButtonSpec,
    ButtonStyle,
    CycleProgress,
    MultilineTextInput,
    TaskScroll,
    TextInput,
)


@pytest.fixture(scope="module")
def canvas():
    pygame.init()
    pygame.display.set_mode((10, 10))
    return UiCanvas(pygame.Surface((300, 200)), FontSet())


def mouse(kind, pos, button=1):
    return pygame.event.Event(kind, pos=pos, button=button)


def key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


class TestButton:
    def make(self, enabled=True):
        calls = []
        spec = ButtonSpec("OK", lambda: calls.append(1), ButtonStyle.GREEN, enabled)
        return Button((10, 10, 80, 24), spec), calls

    def test_hover_follows_the_pointer(self):
        button, _ = self.make()
        button.handle_event(mouse(pygame.MOUSEMOTION, (20, 20)))
        assert button.hovered
        button.handle_event(mouse(pygame.MOUSEMOTION, (200, 200)))
        assert not button.hovered

    def test_click_runs_the_action_on_release_inside(self):
        button, calls = self.make()
        button.handle_event(mouse(pygame.MOUSEBUTTONDOWN, (20, 20)))
        assert button.pressed
        assert button.handle_event(mouse(pygame.MOUSEBUTTONUP, (20, 20)))
        assert calls == [1] and not button.pressed

    def test_releasing_outside_cancels_the_click(self):
        button, calls = self.make()
        button.handle_event(mouse(pygame.MOUSEBUTTONDOWN, (20, 20)))
        assert not button.handle_event(mouse(pygame.MOUSEBUTTONUP, (250, 20)))
        assert calls == []

    def test_a_disabled_button_does_nothing(self):
        button, calls = self.make(enabled=False)
        button.handle_event(mouse(pygame.MOUSEBUTTONDOWN, (20, 20)))
        button.handle_event(mouse(pygame.MOUSEBUTTONUP, (20, 20)))
        assert calls == []

    def test_only_the_left_button_counts(self):
        button, calls = self.make()
        button.handle_event(mouse(pygame.MOUSEBUTTONDOWN, (20, 20), button=3))
        button.handle_event(mouse(pygame.MOUSEBUTTONUP, (20, 20), button=3))
        assert calls == []

    def test_it_draws_pressed_and_hovered(self, canvas):
        button, _ = self.make()
        button.handle_event(mouse(pygame.MOUSEMOTION, (20, 20)))
        button.draw(canvas)
        button.handle_event(mouse(pygame.MOUSEBUTTONDOWN, (20, 20)))
        button.draw(canvas)


def test_button_row_shares_the_width_equally():
    specs = [ButtonSpec(str(i), lambda: None) for i in range(3)]
    buttons = ButtonRow(pygame.Rect(0, 100, 100, 24)).build(specs)
    assert [b.rect.w for b in buttons] == [30, 30, 30]
    assert [b.rect.x for b in buttons] == [0, 34, 68]
    assert all(b.rect.y == 100 and b.rect.h == 24 for b in buttons)


class TestTextInput:
    def make(self, cls=TextInput):
        field = cls((0, 0, 100, 20), "hint", 10)
        field.focused = True
        return field

    def test_typing_appends_up_to_the_limit(self):
        field = self.make()
        for _ in range(6):
            field.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="abc"))
        assert field.text == "abcabcabcabc"

    def test_unfocused_fields_ignore_typing(self):
        field = self.make()
        field.focused = False
        assert not field.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="x"))
        assert field.text == ""

    def test_clicking_moves_the_focus(self):
        field = self.make()
        field.handle_event(mouse(pygame.MOUSEBUTTONDOWN, (500, 500)))
        assert not field.focused
        assert field.handle_event(mouse(pygame.MOUSEBUTTONDOWN, (5, 5)))
        assert field.focused

    def test_backspace_removes_a_character(self, monkeypatch):
        monkeypatch.setattr(pygame.key, "get_mods", lambda: 0)
        field = self.make()
        field.text = "abc"
        field.handle_event(key(pygame.K_BACKSPACE))
        assert field.text == "ab"

    def test_ctrl_backspace_removes_a_word(self, monkeypatch):
        monkeypatch.setattr(pygame.key, "get_mods", lambda: pygame.KMOD_CTRL)
        field = self.make()
        field.text = "hello world"
        field.handle_event(key(pygame.K_BACKSPACE))
        assert field.text == "hello "

    def test_enter_submits(self, monkeypatch):
        monkeypatch.setattr(pygame.key, "get_mods", lambda: 0)
        field = self.make()
        sent = []
        field.on_submit(lambda: sent.append(field.text))
        field.text = "go"
        assert field.handle_event(key(pygame.K_RETURN))
        assert sent == ["go"]

    def test_paste_joins_lines_in_a_single_line_field(self, monkeypatch):
        monkeypatch.setattr(pygame.key, "get_mods", lambda: pygame.KMOD_CTRL)
        monkeypatch.setattr(pygame.scrap, "get_text", lambda: "a\nb")
        field = self.make()
        field.handle_event(key(pygame.K_v))
        assert field.text == "a b"

    def test_a_multiline_field_keeps_the_line_breaks_when_pasting(self, monkeypatch):
        monkeypatch.setattr(pygame.key, "get_mods", lambda: pygame.KMOD_CTRL)
        monkeypatch.setattr(pygame.scrap, "get_text", lambda: "a\nb")
        field = self.make(MultilineTextInput)
        field.handle_event(key(pygame.K_v))
        assert field.text == "a\nb"

    def test_tab_and_escape_are_left_to_the_page(self, monkeypatch):
        monkeypatch.setattr(pygame.key, "get_mods", lambda: 0)
        field = self.make()
        assert not field.handle_event(key(pygame.K_TAB))
        assert not field.handle_event(key(pygame.K_ESCAPE))

    def test_it_draws_placeholder_text_and_caret(self, canvas):
        field = self.make()
        field.focused = False
        field.draw(canvas)
        field.focused = True
        field.text = "word " * 30
        field.draw(canvas)
        multiline = self.make(MultilineTextInput)
        multiline.text = "word " * 30
        multiline.draw(canvas)


def test_text_wrapper_breaks_at_spaces_and_oversized_words():
    font = FontSet().body
    width = font.size("hello world")[0]
    assert TextWrapper(font).lines("hello world again", width) == ["hello world", "again"]
    lines = TextWrapper(font).lines("x" * 60, 40)
    assert len(lines) > 1 and "".join(lines) == "x" * 60
    assert TextWrapper(font).lines("a\nb", 100) == ["a", "b"]


class TestBalloon:
    def make(self):
        pygame.init()
        return Balloon(SoundBank(False))

    def test_text_is_typed_out_and_then_held(self):
        balloon = self.make()
        balloon.say("hello", hold=1.0)
        balloon.update(0.0)
        assert balloon.visible and balloon.typing
        balloon.update(1.0)
        assert not balloon.typing
        balloon.update(0.9)
        assert balloon.visible
        balloon.update(0.2)
        assert not balloon.visible

    def test_lines_wait_their_turn(self):
        balloon = self.make()
        balloon.say("one", hold=0.1)
        balloon.say("two", hold=0.1, interrupt=False)
        balloon.update(0.0)
        seen = [balloon.text]
        for _ in range(10):
            balloon.update(0.1)
            seen.append(balloon.text)
        assert seen[0] == "one" and "two" in seen

    def test_an_interrupting_line_replaces_the_queue(self):
        balloon = self.make()
        balloon.say("one")
        balloon.say("two", interrupt=False)
        balloon.say("three")
        balloon.update(0.0)
        assert balloon.text == "three"

    def test_skip_finishes_typing_then_dismisses(self):
        balloon = self.make()
        balloon.say("a longer line to type", hold=5)
        balloon.update(0.0)
        balloon.skip()
        assert not balloon.typing
        balloon.skip()
        balloon.update(0.01)
        assert not balloon.visible

    def test_a_persistent_line_stays_until_something_replaces_it(self):
        balloon = self.make()
        balloon.say("wait", hold=0.1, persist=True)
        for _ in range(20):
            balloon.update(0.5)
        assert balloon.visible

    def test_silence_drops_everything(self):
        balloon = self.make()
        balloon.say("one")
        balloon.say("two", interrupt=False)
        balloon.update(0.0)
        balloon.silence()
        balloon.update(1.0)
        assert not balloon.visible

    def test_it_draws_inside_the_given_area(self, canvas):
        balloon = self.make()
        balloon.say("a long speech " * 8, persist=True)
        balloon.update(0.5)
        balloon.draw(canvas, Point(100, 100), pygame.Rect(6, 4, 250, 200))


def test_task_scroll_never_goes_negative_and_clamps_to_the_list():
    scroll = TaskScroll()
    scroll.by(3)
    assert scroll.offset == 0
    scroll.by(-9)
    assert scroll.clamp(total=10, visible=4) == 6
    assert scroll.clamp(total=2, visible=4) == 0


@pytest.mark.parametrize(
    ("phase", "cycles", "expected"),
    [(Phase.WORK, 6, 2), (Phase.SHORT, 4, 0), (Phase.LONG, 4, 4), (Phase.IDLE, 3, 0), (Phase.VICTORY, 3, 0)],
)
def test_cycle_progress_counts_finished_pomodoros(phase, cycles, expected):
    assert CycleProgress(phase, cycles, 4).finished == expected


@pytest.mark.parametrize(("seconds", "text"), [(0, "00:00"), (59.6, "01:00"), (1500, "25:00"), (-5, "00:00")])
def test_clock_text(seconds, text):
    assert ClockText.format(seconds) == text
