from __future__ import annotations

from tenhut.core import Phase
from tenhut.i18n import t
from tenhut.ui.widgets import ButtonSpec, ButtonStyle

from .main_button_plan import MainButtonPlan


class WorkPlan(MainButtonPlan):
    """During a work block: ask for a pass, add tasks, desert."""

    def applies(self, phase: Phase, pending: int) -> bool:
        return phase is Phase.WORK

    def specs(self, compact: bool) -> list[ButtonSpec]:
        label = t("button.request_pass_short") if compact else t("button.request_pass")
        return [
            ButtonSpec(label, self._judge.open_request, ButtonStyle.YELLOW),
            self._tasks_spec(compact),
            self._desert_spec(),
        ]
