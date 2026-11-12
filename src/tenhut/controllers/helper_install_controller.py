from __future__ import annotations

import threading

from tenhut.core import Phase, Session
from tenhut.game.audio import SoundEffect
from tenhut.i18n import t
from tenhut.services.blocking import Blocker
from tenhut.services.platform import (
    CommandRunner,
    HelperInstaller,
    HelperInstallerFactory,
    OperatingSystem,
    OperationResult,
    SystemIntegration,
)

from .feedback import Feedback
from .reaction import Reaction
from .speech import Speech
from .speech_hold import SpeechHold
from .tickable import Tickable
from .utterance import Utterance


class HelperInstallController(Tickable):
    """Installs the blocking helper on a thread (the system asks for a password) and reports how it went."""

    def __init__(
        self,
        session: Session,
        system: OperatingSystem,
        runner: CommandRunner,
        *,
        integration: SystemIntegration,
        blocker: Blocker,
        speech: Speech,
        feedback: Feedback,
    ) -> None:
        self._session = session
        self._system = system
        self._runner = runner
        self._integration = integration
        self._blocker = blocker
        self._speech = speech
        self._feedback = feedback
        self._installing = False
        self._result: OperationResult | None = None

    @property
    def installing(self) -> bool:
        return self._installing

    @property
    def offered(self) -> bool:
        """The install row shows while blocking is not installed, and never in the middle of a combat."""
        return (
            self._session.phase is not Phase.WORK
            and not self._system.is_windows
            and (self._installing or not self._blocker.helper_installed())
        )

    def install(self) -> None:
        if self._session.phase is Phase.WORK:
            self._speech.say(Utterance(t("speech.install.not_during_combat"), Reaction.ANGRY_POINT))
            return
        if self._installing:
            return
        self._installing = True
        self._result = None
        self._speech.say(Utterance(t("speech.install.confirm_password"), Reaction.NEUTRAL_POINT, SpeechHold.NORMAL))
        threading.Thread(target=self._work, daemon=True, name="install-helper").start()

    def tick(self, dt: float) -> None:
        result, self._result = self._result, None
        if result is None:
            return
        self._installing = False
        if result.ok and self._blocker.helper_installed():
            self._blocker.retry_now()
            self._speech.say(Utterance(t("speech.install.done"), Reaction.HAPPY_THUMBS, SpeechHold.MEDIUM))
            self._feedback.play(SoundEffect.CLICK)
        else:
            reason = result.message or self._blocker.helper_msg
            self._speech.say(
                Utterance(t("speech.install.failed", error=reason), Reaction.THINKING_CHIN, SpeechHold.LONG)
            )

    def _work(self) -> None:
        self._result = self._installer().install()

    def _installer(self) -> HelperInstaller:
        return HelperInstallerFactory.create(self._system, self._runner, self._integration)
