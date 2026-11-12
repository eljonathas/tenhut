from __future__ import annotations

from dataclasses import dataclass

from tenhut.controllers import (
    AttentionController,
    BlockingController,
    BlockingStatus,
    CalibrationController,
    CameraHolder,
    FeedbackController,
    GestureController,
    Greeter,
    HelperInstallController,
    JudgeController,
    JudgeSlot,
    MissionController,
    QuitController,
    RunState,
    SettingsController,
    SpeechController,
    StatusReporter,
    Tickable,
)
from tenhut.ui.pages import PageNavigator

from .camera_controllers import CameraControllers
from .core_controllers import CoreControllers
from .rule_controllers import RuleControllers


@dataclass(frozen=True, slots=True)
class ControllerParts:
    """Every controller, plus the tickers that advance before and after the stage each frame."""

    core: CoreControllers
    rules: RuleControllers
    camera: CameraControllers
    settings: SettingsController
    installer: HelperInstallController
    attention: AttentionController
    reporter: StatusReporter
    greeter: Greeter
    run_state: RunState
    quitting: QuitController
    early_tickers: tuple[Tickable, ...]
    late_tickers: tuple[Tickable, ...]

    @property
    def navigator(self) -> PageNavigator:
        return self.core.navigator

    @property
    def speech(self) -> SpeechController:
        return self.core.speech

    @property
    def feedback(self) -> FeedbackController:
        return self.core.feedback

    @property
    def gestures(self) -> GestureController:
        return self.core.gestures

    @property
    def judge_slot(self) -> JudgeSlot:
        return self.core.judge_slot

    @property
    def mission(self) -> MissionController:
        return self.rules.mission

    @property
    def judge(self) -> JudgeController:
        return self.rules.judge

    @property
    def blocking(self) -> BlockingController:
        return self.rules.blocking

    @property
    def blocking_status(self) -> BlockingStatus:
        return self.rules.blocking_status

    @property
    def calibration(self) -> CalibrationController:
        return self.camera.calibration

    @property
    def camera_holder(self) -> CameraHolder:
        return self.camera.holder
