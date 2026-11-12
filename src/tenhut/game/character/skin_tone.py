from __future__ import annotations

from dataclasses import dataclass

from ..painting import Rgb
from .character_palette import CharacterPalette


@dataclass(frozen=True, slots=True)
class SkinTone:
    """The three skin colours a face is painted with."""

    base: Rgb
    shade: Rgb
    highlight: Rgb

    @classmethod
    def natural(cls) -> SkinTone:
        return cls(CharacterPalette.SKIN, CharacterPalette.SKIN_SHADE, CharacterPalette.SKIN_HIGHLIGHT)

    @classmethod
    def flushed(cls) -> SkinTone:
        """Red with rage: no highlight, the nose is as red as the rest."""
        return cls(CharacterPalette.SKIN_FLUSHED, CharacterPalette.SKIN_FLUSHED_SHADE, CharacterPalette.SKIN_FLUSHED)
