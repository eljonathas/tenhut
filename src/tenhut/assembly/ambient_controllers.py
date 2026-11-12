from __future__ import annotations

from dataclasses import dataclass

from tenhut.controllers import AttentionController, ChatterController


@dataclass(frozen=True, slots=True)
class AmbientControllers:
    """The controllers that make the general feel alive: his remarks and his attention."""

    chatter: ChatterController
    attention: AttentionController
