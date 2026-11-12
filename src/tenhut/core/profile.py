from __future__ import annotations

from typing import TYPE_CHECKING

from .rank import Rank
from .rank_ladder import RankLadder

if TYPE_CHECKING:
    from .profile_store import ProfileStore


class Profile:
    """The soldier's career: persistent XP and the rank it earns."""

    def __init__(
        self,
        xp: int = 0,
        pomodoros: int = 0,
        missions: int = 0,
        *,
        store: ProfileStore | None = None,
        ladder: RankLadder | None = None,
    ) -> None:
        self._xp = xp
        self._pomodoros = pomodoros
        self._missions = missions
        self._store = store
        self._ladder = ladder or RankLadder.standard()

    @property
    def xp(self) -> int:
        return self._xp

    @property
    def pomodoros(self) -> int:
        return self._pomodoros

    @property
    def missions(self) -> int:
        return self._missions

    @property
    def rank_index(self) -> int:
        return self._ladder.index_for(self._xp)

    @property
    def rank(self) -> Rank:
        return self._ladder.rank_for(self._xp)

    @property
    def next_rank(self) -> Rank | None:
        return self._ladder.next_after(self._xp)

    @property
    def progress(self) -> float:
        """How far through the current rank, 0.0 to 1.0 (1.0 at the top rank)."""
        upcoming = self.next_rank
        if upcoming is None:
            return 1.0
        return (self._xp - self.rank.min_xp) / max(1, upcoming.min_xp - self.rank.min_xp)

    def add_xp(self, amount: int, *, pomodoro: bool = False, mission: bool = False) -> bool:
        """Add XP, save, and say whether the soldier was promoted."""
        before = self.rank_index
        self._xp += amount
        self._pomodoros += int(pomodoro)
        self._missions += int(mission)
        self.save()
        return self.rank_index > before

    def save(self) -> None:
        if self._store is not None:
            self._store.save(self)

    def to_dict(self) -> dict[str, int]:
        return {"xp": self._xp, "pomodoros": self._pomodoros, "missions": self._missions}
