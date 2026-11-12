from __future__ import annotations

import re

from ...core import BlockGroup


class GroupMatcher:
    """Finds the groups a free-text target ("youtu.be", "discord do trabalho") refers to."""

    WORD = re.compile(r"[a-z0-9+]+")
    GENERIC_LABELS = frozenset({"com", "br", "net", "org", "tv", "gg", "be", "it", "co", "www", "m", "app", "io"})
    MIN_FUZZY_LENGTH = 4

    def __init__(self, groups: tuple[BlockGroup, ...]) -> None:
        self._groups = groups

    def match(self, target: str) -> list[str]:
        words = self.WORD.findall(target.lower())
        return [group.name for group in self._groups if self._matches(group, words)]

    def _keys(self, group: BlockGroup) -> set[str]:
        keys = set(self.WORD.findall(group.name.lower()))
        for domain in group.domains:
            keys |= {label for label in domain.lower().split(".") if label not in self.GENERIC_LABELS}
        return keys

    def _matches(self, group: BlockGroup, words: list[str]) -> bool:
        keys = self._keys(group)
        return any(self._similar(word, key) for word in words for key in keys)

    def _similar(self, word: str, key: str) -> bool:
        if word == key:
            return True
        long_enough = len(word) >= self.MIN_FUZZY_LENGTH and len(key) >= self.MIN_FUZZY_LENGTH
        return long_enough and (word in key or key in word)
