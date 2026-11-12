from __future__ import annotations

from tenhut.core import Phase
from tenhut.i18n import t
from tenhut.ui.widgets import ButtonSpec, ButtonStyle

from .main_button_plan import MainButtonPlan


class BreakPlan(MainButtonPlan):
    """During a break: go back to work early, add tasks, desert."""

    def applies(self, phase: Phase, pending: int) -> bool:
        return phase.is_break

    def specs(self, compact: bool) -> list[ButtonSpec]:
        label = t("button.work_short") if compact else t("button.back_to_work")
        return [
            ButtonSpec(label, self._mission.skip_break, ButtonStyle.GREEN),
            self._tasks_spec(compact),
            self._desert_spec(),
        ]
