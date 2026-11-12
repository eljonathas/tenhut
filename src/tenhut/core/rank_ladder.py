from __future__ import annotations

from .rank import Rank


class RankLadder:
    """The ordered ranks (1 XP per pomodoro, +2 per accomplished mission)."""

    def __init__(self, ranks: tuple[Rank, ...]) -> None:
        self._ranks = ranks

    @classmethod
    def standard(cls) -> RankLadder:
        return cls(
            (
                Rank(0, "rank.recruit"),
                Rank(3, "rank.private"),
                Rank(8, "rank.corporal"),
                Rank(15, "rank.sergeant"),
                Rank(25, "rank.lieutenant"),
                Rank(40, "rank.captain"),
                Rank(60, "rank.major"),
                Rank(85, "rank.colonel"),
                Rank(120, "rank.general"),
            )
        )

    @property
    def ranks(self) -> tuple[Rank, ...]:
        return self._ranks

    def index_for(self, xp: int) -> int:
        return max(i for i, rank in enumerate(self._ranks) if xp >= rank.min_xp)

    def rank_for(self, xp: int) -> Rank:
        return self._ranks[self.index_for(xp)]

    def next_after(self, xp: int) -> Rank | None:
        index = self.index_for(xp) + 1
        return self._ranks[index] if index < len(self._ranks) else None
