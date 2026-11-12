from __future__ import annotations

from dataclasses import dataclass

from tenhut.controllers import (
    BlockingController,
    BlockingStatus,
    CareerController,
    HelperInstallController,
    JudgeController,
    MissionController,
    PomodoroController,
)


@dataclass(frozen=True, slots=True)
class RuleControllers:
    """The controllers that enforce the rules of the game: blocking, missions, the pomodoro clock and the judge."""

    blocking: BlockingController
    blocking_status: BlockingStatus
    career: CareerController
    mission: MissionController
    pomodoro: PomodoroController
    judge: JudgeController
    installer: HelperInstallController
