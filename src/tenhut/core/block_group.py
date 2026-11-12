from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BlockGroup:
    """A named set of distractions: domains (www./m. variants are automatic) and processes to close."""

    name: str
    domains: tuple[str, ...] = ()
    apps: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, list[str]]:
        return {"domains": list(self.domains), "apps": list(self.apps)}
