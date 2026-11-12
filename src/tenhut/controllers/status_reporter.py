from __future__ import annotations

from tenhut.core import Clock, Phase, Session
from tenhut.i18n import t
from tenhut.ui.painting import ClockText

from .active_settings import ActiveSettings
from .blocking_status import BlockingStatus
from .camera.camera_controller import CameraController
from .judge_slot import JudgeSlot
from .severity import Severity
from .status_line import StatusLine


class StatusReporter:
    """Works out what the status area of the board and the mini HUD have to say right now."""

    MAX_LINES = 4

    def __init__(
        self,
        session: Session,
        settings: ActiveSettings,
        clock: Clock,
        *,
        judge: JudgeSlot,
        camera: CameraController,
        blocking: BlockingStatus,
    ) -> None:
        self._session = session
        self._settings = settings
        self._clock = clock
        self._judge = judge
        self._camera = camera
        self._blocking = blocking

    def lines(self) -> list[StatusLine]:
        session, now = self._session, self._clock.now()
        lines: list[StatusLine] = []
        if session.phase is Phase.IDLE and session.pending_count():
            lines.append(StatusLine(t("status.line.mission_paused", n=session.pending_count()), Severity.NOTICE))
        for group, expires in sorted(session.active_grants(now).items()):
            lines.append(
                StatusLine(
                    t("status.line.unblocked", group=group, time=ClockText.format(expires - now)), Severity.SUCCESS
                )
            )
        if self._judge.waiting_without_ai:
            lines.append(
                StatusLine(t("status.line.patience", time=ClockText.format(self._patience_left(now))), Severity.NOTICE)
            )
        lines.extend(self._combat_lines(now))
        return lines[: self.MAX_LINES]

    def hud_notice(self) -> StatusLine | None:
        """The single note the mini HUD has room for."""
        now = self._clock.now()
        grants = self._session.active_grants(now)
        if grants:
            group, expires = min(grants.items(), key=lambda grant: grant[1])
            return StatusLine(f"{group} {ClockText.format(expires - now)}", Severity.SUCCESS)
        if self._judge.waiting_without_ai:
            return StatusLine(
                t("status.hud.patience", time=ClockText.format(self._patience_left(now))), Severity.NOTICE
            )
        if self._camera.active and self._camera.status.is_alert:
            return StatusLine(self._camera.status.text.lower(), Severity.ALERT)
        return None

    def _patience_left(self, now: float) -> float:
        job = self._judge.job
        return self._settings.current.judge.local_wait_seconds - (now - job.started_at)

    def _combat_lines(self, now: float) -> list[StatusLine]:
        session = self._session
        if session.phase is not Phase.WORK:
            return []
        lines: list[StatusLine] = []
        if now < session.denied_until:
            lines.append(
                StatusLine(
                    t("status.line.next_request", time=ClockText.format(session.denied_until - now)), Severity.WARNING
                )
            )
        if self._camera.active:
            lines.append(self._camera_line())
        if not self._blocking.helper_installed:
            lines.append(StatusLine(t("status.line.blocking_inactive", hint=self._blocking.hint), Severity.ALERT))
        return lines

    def _camera_line(self) -> StatusLine:
        status = self._camera.status
        line = t("status.line.camera", state=status.text if status.present else t("status.line.camera_starting"))
        if self._session.infractions:
            line += t("status.line.infractions", n=self._session.infractions)
        return StatusLine(line, Severity.WARNING if status.is_alert else Severity.MUTED)
