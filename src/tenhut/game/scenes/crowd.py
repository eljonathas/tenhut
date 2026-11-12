from __future__ import annotations

from ..painting import Canvas
from .crowd_member import CrowdMember
from .parade_frame import ParadeFrame


class Crowd:
    """The spectators lining the street, drawn from far to near so the front rows overlap the back rows."""

    WAVE_EVERY = 3

    def __init__(self, members: list[CrowdMember]) -> None:
        self._members = sorted(members, key=lambda member: member.scale)

    def __len__(self) -> int:
        return len(self._members)

    def draw(self, canvas: Canvas, frame: ParadeFrame) -> None:
        for index, member in enumerate(self._members):
            member.draw(canvas, frame, waving=index % self.WAVE_EVERY == 0 or frame.party)
