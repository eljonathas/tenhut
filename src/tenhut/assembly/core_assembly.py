from __future__ import annotations

from tenhut.controllers import (
    DistractionTracker,
    FeedbackController,
    GestureController,
    JudgeSlot,
    SpeechController,
)
from tenhut.ui.pages import PageNavigator

from .core_controllers import CoreControllers
from .platform_parts import PlatformParts
from .world_parts import WorldParts


class CoreAssembly:
    """Creates the navigator, the speech, the feedback and the gestures."""

    def __init__(self, platform: PlatformParts, world: WorldParts) -> None:
        self._platform = platform
        self._world = world

    def assemble(self) -> CoreControllers:
        navigator = PageNavigator(self._world.screen)
        slot, tracker = JudgeSlot(), DistractionTracker()
        speech = self._speech(slot, tracker)
        feedback = self._feedback(navigator)
        gestures = GestureController(
            general=self._world.general,
            layouts=self._world.screen,
            fonts=self._world.fonts,
            speech=speech,
            feedback=feedback,
            navigation=navigator,
        )
        return CoreControllers(navigator, slot, tracker, speech, feedback, gestures)

    def _speech(self, slot: JudgeSlot, tracker: DistractionTracker) -> SpeechController:
        world = self._world
        return SpeechController(
            balloon=world.balloon,
            general=world.general,
            session=world.session,
            clock=self._platform.clock,
            judge=slot,
            distraction=tracker,
        )

    def _feedback(self, navigator: PageNavigator) -> FeedbackController:
        platform, world = self._platform, self._world
        return FeedbackController(
            sounds=world.sounds,
            notifier=platform.notifier,
            settings=platform.settings,
            fonts=world.fonts,
            clock=platform.clock,
            layouts=world.screen,
            navigation=navigator,
        )
