from __future__ import annotations

from tenhut.core import Clock, Phase, Session
from tenhut.game.audio import SoundEffect
from tenhut.i18n import t
from tenhut.services.blocking import Blocker, ProcessKiller

from .active_settings import ActiveSettings
from .enforcement import Enforcement
from .feedback import Feedback
from .gestures import Gestures
from .reaction import Reaction
from .speech import Speech
from .tickable import Tickable
from .utterance import Utterance


class BlockingController(Enforcement, Tickable):
    """Keeps the blocked sites and apps shut while a work block is on, and notices passes that run out."""

    MIN_INTERVAL = 1.0
    REASSERT_INTERVAL = 60
    KILL_INTERVAL = 3
    CLOSED_APPS_SECONDS = 3

    def __init__(
        self,
        session: Session,
        settings: ActiveSettings,
        clock: Clock,
        *,
        blocker: Blocker,
        killer: ProcessKiller,
        speech: Speech,
        feedback: Feedback,
        gestures: Gestures,
    ) -> None:
        self._session = session
        self._settings = settings
        self._clock = clock
        self._blocker = blocker
        self._killer = killer
        self._speech = speech
        self._feedback = feedback
        self._gestures = gestures
        self._last_enforced = 0.0
        self._last_kill = 0.0
        self._last_reassert = clock.now()
        self._previous_grants: set[str] = set()

    def tick(self, dt: float) -> None:
        self.enforce()

    def enforce(self, force: bool = False) -> None:
        now = self._clock.now()
        if not force and now - self._last_enforced < self.MIN_INTERVAL:
            return
        self._last_enforced = now
        if self._session.phase is Phase.WORK:
            self._block(now)
        else:
            self._blocker.apply([])
        self._announce_expired_passes(now)

    def lock_for_exit(self) -> None:
        """Without the app running nobody re-blocks at the end of a break, so everything is blocked right now."""
        if self._session.in_mission:
            block_list = self._settings.current.block_list
            self._blocker.apply_now(block_list.domains_for(block_list.names))

    def _block(self, now: float) -> None:
        settings = self._settings.current
        block_list = settings.block_list
        if now - self._last_reassert > self.REASSERT_INTERVAL:
            self._blocker.reassert()
            self._last_reassert = now
        blocked = set(block_list.names) - set(self._session.active_grants(now))
        self._blocker.apply(block_list.domains_for(blocked))
        if settings.close_blocked_apps and now - self._last_kill > self.KILL_INTERVAL:
            self._last_kill = now
            self._close_apps(block_list.apps_for(blocked))

    def _close_apps(self, apps: list[str]) -> None:
        closed = self._killer.kill(apps)
        if not closed:
            return
        self._speech.say(
            Utterance(
                t("speech.blocking.closed_apps", apps=", ".join(closed).title()),
                Reaction.ANGRY_POINT,
                self.CLOSED_APPS_SECONDS,
            )
        )
        self._feedback.play(SoundEffect.DENIED)
        self._gestures.poke(2)

    def _announce_expired_passes(self, now: float) -> None:
        active = set(self._session.active_grants(now))
        expired = self._previous_grants - active
        if expired and self._session.phase is Phase.WORK:
            self._speech.say(
                Utterance(t("speech.blocking.pass_expired", groups=", ".join(sorted(expired))), Reaction.STERN_POINT)
            )
            self._feedback.play(SoundEffect.ALARM)
            self._gestures.poke(1)
        self._previous_grants = active
