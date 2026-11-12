from __future__ import annotations

from tenhut.core import Phase
from tenhut.i18n import t
from tenhut.ui.widgets import ButtonSpec, ButtonStyle

from .main_button_plan import MainButtonPlan


class PausedPlan(MainButtonPlan):
    """A mission was interrupted (a desertion was accepted): resume the same list or start another."""

    def applies(self, phase: Phase, pending: int) -> bool:
        return phase is Phase.IDLE and pending > 0

    def specs(self, compact: bool) -> list[ButtonSpec]:
        specs = [
            ButtonSpec(t("button.resume"), self._mission.resume_mission, ButtonStyle.GREEN),
            self._fresh_spec(compact),
        ]
        if compact:
            specs.append(self._tasks_spec(compact))
        specs.append(self._settings_spec())
        return specs

    def _fresh_spec(self, compact: bool) -> ButtonSpec:
        if self._mission.confirming_discard:
            return ButtonSpec(t("button.confirm"), self._mission.fresh_mission, ButtonStyle.RED)
        label = t("button.new_mission_short") if compact else t("button.new_mission")
        return ButtonSpec(label, self._mission.fresh_mission, ButtonStyle.TAN)
