from __future__ import annotations

from tenhut.core import Clock
from tenhut.game.animations import FloatingTextStack, Stamp, StampContent
from tenhut.game.audio import SoundBank, SoundEffect
from tenhut.game.painting import Palette, Rgb
from tenhut.services.platform import Notifier
from tenhut.ui.fonts import FontSet
from tenhut.ui.layout import LayoutProvider

from .active_settings import ActiveSettings
from .feedback import Feedback
from .navigation import Navigation
from .tickable import Tickable


class FeedbackController(Feedback, Tickable):
    """Sounds, desktop notifications, the rubber stamp, floating texts and the red flash."""

    def __init__(
        self,
        sounds: SoundBank,
        notifier: Notifier,
        settings: ActiveSettings,
        *,
        fonts: FontSet,
        clock: Clock,
        layouts: LayoutProvider,
        navigation: Navigation,
    ) -> None:
        self._sounds = sounds
        self._notifier = notifier
        self._settings = settings
        self._fonts = fonts
        self._clock = clock
        self._layouts = layouts
        self._navigation = navigation
        self._popups = FloatingTextStack(fonts.title)
        self._stamp: Stamp | None = None
        self._flash = 0.0
        self._shake_until = 0.0

    @property
    def popups(self) -> FloatingTextStack:
        return self._popups

    @property
    def stamp(self) -> Stamp | None:
        """The stamp on screen, if it has not faded out yet."""
        if self._stamp is not None and self._stamp.finished:
            self._stamp = None
        return self._stamp

    @property
    def flash_level(self) -> float:
        return self._flash

    @property
    def screen_shaking(self) -> bool:
        return self._clock.now() < self._shake_until

    def play(self, effect: SoundEffect) -> None:
        self._sounds.play(effect)

    def notify(self, title: str, body: str, urgent: bool = False) -> None:
        if self._settings.current.notifications_enabled:
            self._notifier.notify(title, body, urgent)

    def show_stamp(self, message: str, color: Rgb) -> None:
        placement = self._layouts.layout.stamp_placement(self._navigation.board_shown)
        self._stamp = Stamp(StampContent(message, color), self._fonts.title, self._clock, placement=placement)

    def popup(self, message: str, color: Rgb = Palette.GOLD_LIGHT) -> None:
        self._popups.pop_up(message, color)

    def flash(self, level: float) -> None:
        self._flash = level

    def shake_screen(self, seconds: float) -> None:
        self._shake_until = self._clock.now() + seconds

    def tick(self, dt: float) -> None:
        self._flash = max(0.0, self._flash - dt)
        self._popups.update(dt)
