from __future__ import annotations

from tenhut.game.animations import PokeAnimation, PokeTrajectory, SlamAnimation
from tenhut.game.audio import SoundEffect
from tenhut.game.character import Character, Mood, PoseName
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.fonts import FontSet
from tenhut.ui.layout import Layout, LayoutProvider

from .feedback import Feedback
from .gestures import Gestures
from .navigation import Navigation
from .speech import Speech
from .tickable import Tickable


class GestureController(Gestures, Tickable):
    """The poke through the screen and the desk slam: starts them and plays them out."""

    REACH_WIDTH_SHARE = 0.4
    REACH_HEIGHT_SHARE = 0.42
    EDGE_MARGIN = 4
    TARGET_HALF_REACH = 0.5
    TARGET_LOW_REACH = 0.35
    SIDE_DRIFT = 2
    DROP = 8
    SLEEVE_WIDTH = 10
    SLEEVE_TAPER = 4
    ANIMATION_HOLD = 0.3
    POKE_SHAKE = 0.18
    SLAM_SHAKE = 0.22

    def __init__(
        self,
        general: Character,
        layouts: LayoutProvider,
        fonts: FontSet,
        *,
        speech: Speech,
        feedback: Feedback,
        navigation: Navigation,
    ) -> None:
        self._general = general
        self._layouts = layouts
        self._fonts = fonts
        self._speech = speech
        self._feedback = feedback
        self._navigation = navigation
        self._poke: PokeAnimation | None = None
        self._slam: SlamAnimation | None = None

    @property
    def poke_active(self) -> bool:
        return self._poke is not None

    @property
    def poke_animation(self) -> PokeAnimation | None:
        return self._poke

    @property
    def slam(self) -> SlamAnimation | None:
        return self._slam

    def poke(self, jabs: int = 1) -> None:
        layout = self._layouts.layout
        if self._poke or self._slam is not None or (layout.compact and self._navigation.board_shown):
            return
        self._poke = PokeAnimation(self._trajectory(layout), jabs, caption=t("popup.poke_hit"), font=self._fonts.title)
        self._general.snap(alert=False)

    def start_slam(self) -> None:
        self._poke = None
        self._slam = SlamAnimation(self._layouts.layout.slam_placement(), t("popup.slam_hit"), self._fonts.title)

    def cancel_poke(self) -> None:
        self._poke = None

    def tick(self, dt: float) -> None:
        if self._poke:
            self._play_poke(dt)
        if self._slam is not None:
            self._play_slam(dt)

    def _trajectory(self, layout: Layout) -> PokeTrajectory:
        scene, scale = layout.scene, layout.general_scale
        shoulder = layout.shoulder
        reach = min(scene.w * self.REACH_WIDTH_SHARE, scene.h * self.REACH_HEIGHT_SHARE)
        target = Point(
            max(scene.x + reach * self.TARGET_HALF_REACH + self.EDGE_MARGIN, shoulder.x - self.SIDE_DRIFT * scale),
            min(scene.bottom - reach * self.TARGET_LOW_REACH, shoulder.y + self.DROP * scale),
        )
        return PokeTrajectory(shoulder, target, self.SLEEVE_WIDTH * scale, reach, self.SLEEVE_TAPER * scale)

    def _play_poke(self, dt: float) -> None:
        poke = self._poke
        assert poke is not None
        self._general.show(pose=PoseName.POKE)
        self._speech.keep_reacting(self.ANIMATION_HOLD)
        poke.update(dt)
        for _ in range(poke.jabs_landed):
            self._feedback.play(SoundEffect.TOC)
            self._feedback.shake_screen(self.POKE_SHAKE)
        if poke.finished:
            self._poke = None
            self._general.show(pose=PoseName.POINT)

    def _play_slam(self, dt: float) -> None:
        slam = self._slam
        assert slam is not None
        slam.update(dt)
        self._general.show(Mood.ANGRY, PoseName.FISTS_UP if slam.fists_raised else PoseName.SLAM)
        self._speech.keep_reacting(self.ANIMATION_HOLD)
        if slam.impact_landed:
            self._feedback.play(SoundEffect.SLAM)
            self._feedback.shake_screen(self.SLAM_SHAKE)
        if slam.finished:
            self._slam = None
            self._general.show(Mood.ANGRY, PoseName.POINT)
