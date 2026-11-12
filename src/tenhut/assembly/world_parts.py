from __future__ import annotations

from dataclasses import dataclass

from tenhut.core import Profile, Session
from tenhut.game.audio import SoundBank
from tenhut.game.character import Character
from tenhut.game.random_source import RandomSource
from tenhut.game.scenes import SceneRegistry
from tenhut.services.blocking import Blocker
from tenhut.ui.fonts import FontSet
from tenhut.ui.layout import LogicalScreen
from tenhut.ui.stage import DisplayWindow
from tenhut.ui.widgets import Balloon


@dataclass(frozen=True, slots=True)
class WorldParts:
    """The things the game is made of: the window, the fonts, the sounds, the general and the scenery."""

    window: DisplayWindow
    screen: LogicalScreen
    fonts: FontSet
    sounds: SoundBank
    balloon: Balloon
    general: Character
    scenes: SceneRegistry
    blocker: Blocker
    session: Session
    profile: Profile
    randomness: RandomSource
