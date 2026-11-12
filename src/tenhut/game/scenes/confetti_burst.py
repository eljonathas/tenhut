from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..painting import Canvas, Rgb
from ..random_source import RandomSource


@dataclass(slots=True)
class _Piece:
    x: float
    y: float
    vx: float
    vy: float
    color: Rgb


class ConfettiBurst:
    """Confetti thrown over the desk on promotions and victory; it falls past the bottom and is gone."""

    PIECES: ClassVar[int] = 120
    PIECE_SIZE: ClassVar[int] = 2
    COLORS: ClassVar[tuple[Rgb, ...]] = (
        Rgb(240, 80, 80),
        Rgb(250, 214, 90),
        Rgb(90, 170, 90),
        Rgb(90, 140, 220),
        Rgb(240, 240, 240),
    )

    def __init__(self) -> None:
        self._pieces: list[_Piece] = []

    def throw(self, center_x: float, randomness: RandomSource) -> None:
        for _ in range(self.PIECES):
            self._pieces.append(
                _Piece(
                    center_x + randomness.uniform(-70, 70),
                    randomness.uniform(-80, 0),
                    randomness.uniform(-8, 8),
                    randomness.uniform(20, 50),
                    randomness.choice(self.COLORS),
                )
            )

    def fall(self, dt: float, world_height: int) -> None:
        for piece in self._pieces:
            piece.x += piece.vx * dt
            piece.y += piece.vy * dt
        self._pieces = [piece for piece in self._pieces if piece.y < world_height]

    def draw(self, canvas: Canvas) -> None:
        width, height = canvas.surface.get_size()
        for piece in self._pieces:
            if 0 <= piece.x < width and 0 <= piece.y < height:
                canvas.rect(piece.color, (int(piece.x), int(piece.y), self.PIECE_SIZE, self.PIECE_SIZE))
