"""Test doubles for the injected collaborators."""

from __future__ import annotations

from tenhut.controllers import (
    Celebration,
    Enforcement,
    Feedback,
    Gestures,
    Navigation,
    PageId,
    Speech,
    Utterance,
)
from tenhut.core import Clock
from tenhut.game.audio import SoundEffect
from tenhut.game.painting import Palette, Rgb
from tenhut.services.blocking import HostsBackend, HostsError
from tenhut.services.platform import CommandError, CommandResult, CommandRunner, CommandSpec
from tenhut.ui.layout import Layout, LayoutFactory, LayoutProvider, Size


class FakeClock(Clock):
    def __init__(self, now: float = 1000.0) -> None:
        self.current = now
        self.slept: list[float] = []

    def now(self) -> float:
        return self.current

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.current += seconds


class FakeRunner(CommandRunner):
    """Records the commands; answers with `result`, or raises `error`."""

    def __init__(self, result: CommandResult | None = None, error: CommandError | None = None) -> None:
        self.result = result or CommandResult(0)
        self.error = error
        self.ran: list[CommandSpec] = []
        self.launched: list[CommandSpec] = []

    def run(self, spec: CommandSpec) -> CommandResult:
        self.ran.append(spec)
        if self.error:
            raise self.error
        return self.result

    def launch(self, spec: CommandSpec) -> None:
        self.launched.append(spec)
        if self.error:
            raise self.error


class FakeBackend(HostsBackend):
    """Records every write; fails the first `failures` writes."""

    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.calls: list[list[str]] = []
        self.is_available = True

    def available(self) -> bool:
        return self.is_available

    def status_message(self) -> str:
        return "" if self.is_available else "not installed"

    def apply(self, domains: list[str]) -> None:
        self.calls.append(list(domains))
        if self.failures > 0:
            self.failures -= 1
            raise HostsError("boom")

    def clear(self) -> None:
        self.apply([])


class FakeRandom:
    """Always answers the same: ``uniform`` the low bound, ``random`` a fixed number, ``choice`` the first option."""

    def __init__(self, value: float = 0.0) -> None:
        self.value = value

    def random(self) -> float:
        return self.value

    def uniform(self, low: float, high: float) -> float:
        return low

    def randint(self, low: int, high: int) -> int:
        return low

    def randrange(self, start: int, stop: int) -> int:
        return start

    def choice(self, options):
        return options[0]


class FakeSpeech(Speech):
    """Records what the general was asked to say."""

    def __init__(self) -> None:
        self.said: list[Utterance] = []
        self.queued: list[str] = []
        self.murmured: list[str] = []
        self.reactions: list[float] = []

    @property
    def messages(self) -> list[str]:
        return [utterance.message for utterance in self.said]

    def say(self, utterance: Utterance) -> None:
        self.said.append(utterance)

    def say_next(self, message: str) -> None:
        self.queued.append(message)

    def murmur(self, message: str, persist: bool = False) -> None:
        self.murmured.append(message)

    def keep_reacting(self, seconds: float) -> None:
        self.reactions.append(seconds)

    def react_for(self, seconds: float) -> None:
        self.reactions.append(seconds)


class FakeFeedback(Feedback):
    """Records sounds, stamps, popups and notifications."""

    def __init__(self) -> None:
        self.sounds: list[SoundEffect] = []
        self.stamps: list[str] = []
        self.popups: list[str] = []
        self.notifications: list[str] = []
        self.flashes: list[float] = []
        self.shakes: list[float] = []

    def play(self, effect: SoundEffect) -> None:
        self.sounds.append(effect)

    def notify(self, title: str, body: str, urgent: bool = False) -> None:
        self.notifications.append(title)

    def show_stamp(self, message: str, color: Rgb) -> None:
        self.stamps.append(message)

    def popup(self, message: str, color: Rgb = Palette.GOLD_LIGHT) -> None:
        self.popups.append(message)

    def flash(self, level: float) -> None:
        self.flashes.append(level)

    def shake_screen(self, seconds: float) -> None:
        self.shakes.append(seconds)


class FakeNavigation(Navigation):
    """Remembers the pages opened; ``board_shown`` is whatever the test sets."""

    def __init__(self) -> None:
        self.opened: list[PageId] = []
        self.refreshed: list[PageId] = []
        self.current = PageId.MAIN
        self.board = True

    @property
    def current_id(self) -> PageId:
        return self.current

    @property
    def board_shown(self) -> bool:
        return self.board

    def open(self, page_id: PageId) -> None:
        self.opened.append(page_id)
        self.current = page_id

    def refresh(self, page_id: PageId) -> None:
        self.refreshed.append(page_id)


class FakeEnforcement(Enforcement):
    def __init__(self) -> None:
        self.forced = 0

    def enforce(self, force: bool = False) -> None:
        self.forced += force


class FakeGestures(Gestures):
    def __init__(self) -> None:
        self.pokes: list[int] = []
        self.slams = 0

    @property
    def poke_active(self) -> bool:
        return False

    @property
    def slam(self):
        return None

    def poke(self, jabs: int = 1) -> None:
        self.pokes.append(jabs)

    def start_slam(self) -> None:
        self.slams += 1


class FakeCelebration(Celebration):
    def __init__(self) -> None:
        self.bursts: list[float | None] = []

    def fireworks(self, center_x: float | None = None) -> None:
        self.bursts.append(center_x)


class FixedLayouts(LayoutProvider):
    """A layout that never changes."""

    def __init__(self, size: Size | None = None) -> None:
        self._layout = LayoutFactory().create(size or Size(560, 360))

    @property
    def layout(self) -> Layout:
        return self._layout

    def to_logical(self, position: tuple[int, int]) -> tuple[int, int]:
        return position
