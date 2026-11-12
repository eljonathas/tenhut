from __future__ import annotations

from typing import TYPE_CHECKING

from .clock import Clock
from .phase import Phase
from .session_event import SessionEvent
from .settings import Settings
from .system_clock import SystemClock
from .task import Task

if TYPE_CHECKING:
    from .session_store import SessionStore


class Session:
    """The mission state machine: phases, tasks, passes granted by the judge and the penalties."""

    def __init__(self, clock: Clock | None = None, store: SessionStore | None = None) -> None:
        self._clock = clock or SystemClock()
        self._store = store
        self._phase = Phase.IDLE
        self._phase_start = 0.0
        self._phase_end = 0.0
        self._cycles = 0
        self._tasks: list[Task] = []
        self._grants: dict[str, float] = {}
        self._denied_until = 0.0
        self._history: list[str] = []
        self._infractions = 0
        self._mission_start = 0.0

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def phase_start(self) -> float:
        return self._phase_start

    @property
    def phase_end(self) -> float:
        return self._phase_end

    @property
    def cycles(self) -> int:
        return self._cycles

    @property
    def tasks(self) -> tuple[Task, ...]:
        return tuple(self._tasks)

    @property
    def denied_until(self) -> float:
        return self._denied_until

    @property
    def history(self) -> tuple[str, ...]:
        return tuple(self._history)

    @property
    def infractions(self) -> int:
        return self._infractions

    @property
    def mission_start(self) -> float:
        return self._mission_start

    @property
    def in_mission(self) -> bool:
        return self._phase.in_mission

    @property
    def blocking(self) -> bool:
        return self._phase is Phase.WORK

    def remaining(self, now: float | None = None) -> float:
        if not self.in_mission:
            return 0.0
        return max(0.0, self._phase_end - self._at(now))

    def progress(self, now: float | None = None) -> float:
        if not self.in_mission or self._phase_end <= self._phase_start:
            return 0.0
        elapsed = self._at(now) - self._phase_start
        return min(1.0, max(0.0, elapsed / (self._phase_end - self._phase_start)))

    def active_grants(self, now: float | None = None) -> dict[str, float]:
        at = self._at(now)
        return {group: expiry for group, expiry in self._grants.items() if expiry > at}

    def all_done(self) -> bool:
        return bool(self._tasks) and all(t.done for t in self._tasks)

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks if not t.done)

    def done_count(self) -> int:
        return len(self._tasks) - self.pending_count()

    def _at(self, now: float | None) -> float:
        return self._clock.now() if now is None else now

    def add_task(self, text: str) -> None:
        self._tasks.append(Task(text))

    def remove_task(self, index: int) -> None:
        del self._tasks[index]

    def toggle_task(self, index: int) -> Task | None:
        """Flip the task and return it; None when the index is out of range."""
        if not 0 <= index < len(self._tasks):
            return None
        self._tasks[index].toggle()
        return self._tasks[index]

    def clear_tasks(self) -> None:
        self._tasks = []
        self._phase = Phase.IDLE

    def keep_pending_tasks(self) -> None:
        self._tasks = [t for t in self._tasks if not t.done]
        self._phase = Phase.IDLE

    def grant(self, group: str, expires_at: float) -> None:
        self._grants[group] = max(self._grants.get(group, 0.0), expires_at)

    def deny_until(self, timestamp: float) -> None:
        self._denied_until = timestamp

    def log(self, entry: str) -> None:
        self._history.append(entry)

    def record_infraction(self) -> int:
        self._infractions += 1
        return self._infractions

    def penalize(self, minutes: float) -> None:
        if self._phase is Phase.WORK and minutes > 0:
            self._phase_end += minutes * 60

    def start_mission(self, settings: Settings, now: float | None = None) -> None:
        at = self._at(now)
        self._cycles = 0
        self._grants = {}
        self._history = []
        self._infractions = 0
        self._denied_until = 0.0
        self._mission_start = at
        self._enter(Phase.WORK, settings.timer.work_minutes, at)

    def end_mission(self, victory: bool) -> None:
        self._phase = Phase.VICTORY if victory else Phase.IDLE
        self._grants = {}
        self._phase_start = self._phase_end = 0.0

    def skip_break(self, settings: Settings, now: float | None = None) -> None:
        if self._phase.is_break:
            self._enter(Phase.WORK, settings.timer.work_minutes, self._at(now))

    def expire_phase(self, timestamp: float) -> None:
        self._phase_end = timestamp

    def tick(self, settings: Settings, now: float | None = None) -> list[SessionEvent]:
        at = self._at(now)
        if self._phase is Phase.WORK and self.all_done():
            self.end_mission(True)
            return [SessionEvent.VICTORY]
        if not self.in_mission or at < self._phase_end:
            return []
        if self._phase is Phase.WORK:
            self._finish_work_block(settings, at)
            return [SessionEvent.WORK_END]
        self._enter(Phase.WORK, settings.timer.work_minutes, at)
        return [SessionEvent.BREAK_END]

    def _finish_work_block(self, settings: Settings, now: float) -> None:
        timer = settings.timer
        self._cycles += 1
        self._grants = {}
        is_long = self._cycles % timer.cycles_before_long_break == 0
        minutes = timer.long_break_minutes if is_long else timer.short_break_minutes
        # if the app stayed closed, the break starts now instead of vanishing silently
        self._enter(Phase.LONG if is_long else Phase.SHORT, minutes, now)

    def _enter(self, phase: Phase, minutes: float, now: float) -> None:
        self._phase = phase
        self._phase_start = now
        self._phase_end = now + minutes * 60

    def save(self) -> None:
        if self._store is not None:
            self._store.save(self)

    def to_dict(self) -> dict[str, object]:
        return {
            "phase": self._phase.value,
            "phase_start": self._phase_start,
            "phase_end": self._phase_end,
            "cycles": self._cycles,
            "tasks": [t.to_dict() for t in self._tasks],
            "grants": dict(self._grants),
            "denied_until": self._denied_until,
            "history": list(self._history),
            "infractions": self._infractions,
            "mission_start": self._mission_start,
        }

    def restore(self, data: dict[str, object]) -> None:
        """Load the fields of `to_dict`; raises ValueError/TypeError on malformed data."""
        self._phase = Phase(data.get("phase", Phase.IDLE.value))
        self._phase_start = float(data.get("phase_start", 0.0))
        self._phase_end = float(data.get("phase_end", 0.0))
        self._cycles = int(data.get("cycles", 0))
        self._tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        self._grants = {str(g): float(t) for g, t in dict(data.get("grants", {})).items()}
        self._denied_until = float(data.get("denied_until", 0.0))
        self._history = [str(h) for h in data.get("history", [])]
        self._infractions = int(data.get("infractions", 0))
        self._mission_start = float(data.get("mission_start", 0.0))
