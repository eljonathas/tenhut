from __future__ import annotations

from dataclasses import dataclass

from tenhut.controllers import (
    DistractionTracker,
    FeedbackController,
    GestureController,
    JudgeSlot,
    SpeechController,
)
from tenhut.ui.pages import PageNavigator


@dataclass(frozen=True, slots=True)
class CoreControllers:
    """The controllers every other one talks to: navigation, speech, feedback and gestures."""

    navigator: PageNavigator
    judge_slot: JudgeSlot
    tracker: DistractionTracker
    speech: SpeechController
    feedback: FeedbackController
    gestures: GestureController
