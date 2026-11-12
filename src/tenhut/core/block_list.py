from __future__ import annotations

from collections.abc import Iterable

from .block_group import BlockGroup


class BlockList:
    """The configured groups, answering which domains and apps a set of group names covers."""

    def __init__(self, groups: Iterable[BlockGroup]) -> None:
        self._groups = tuple(groups)

    @property
    def names(self) -> list[str]:
        return [g.name for g in self._groups]

    @property
    def groups(self) -> tuple[BlockGroup, ...]:
        return self._groups

    @staticmethod
    def expand(domain: str) -> list[str]:
        """A root domain also covers its `www.` and `m.` variants."""
        d = domain.strip().lower()
        if not d:
            return []
        return [d, f"www.{d}", f"m.{d}"] if d.count(".") == 1 else [d]

    def domains_for(self, names: Iterable[str]) -> list[str]:
        wanted = set(names)
        found = {e for g in self._groups if g.name in wanted for d in g.domains for e in self.expand(d)}
        return sorted(found)

    def apps_for(self, names: Iterable[str]) -> list[str]:
        wanted = set(names)
        return [a for g in self._groups if g.name in wanted for a in g.apps]
