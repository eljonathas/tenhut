from __future__ import annotations

from tenhut.core import MonitorSide
from tenhut.i18n import t

from .base_step import BaseStep
from .calibration_plan import CalibrationPlan
from .calibration_step import CalibrationStep
from .down_step import DownStep
from .side_step import SideStep


class CalibrationPlanner:
    """Plans the calibration: the main screen, every monitor beside it, then looking down."""

    def plan(self, sides: dict[MonitorSide, list[str]]) -> CalibrationPlan:
        steps: list[CalibrationStep] = [BaseStep(t("calibration.step.main_screen"))]
        for side, names in sides.items():
            for name in names:
                prompt = t("calibration.step.side_monitor", side=t(side.label_key).upper(), n=name)
                steps.append(SideStep(prompt, side))
        steps.append(DownStep(t("calibration.step.look_down")))
        return CalibrationPlan(steps)
