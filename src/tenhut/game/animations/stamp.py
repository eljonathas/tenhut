from __future__ import annotations

import pygame

from tenhut.core import Clock

from .clocked_animation import ClockedAnimation
from .stamp_content import StampContent
from .stamp_placement import StampPlacement


class Stamp(ClockedAnimation):
    """A big tilted rubber stamp (APPROVED, DENIED...) that slams down, rests and fades."""

    DURATION = 1.8
    FADE_START = 1.4
    FADE_SECONDS = 0.4
    TILT_DEGREES = 10
    SLAM_SECONDS = 0.18
    SLAM_GROWTH = 6
    LONG_MESSAGE_LENGTH = 9
    BORDER = 3
    PADDING = (16, 10)
    SCREEN_MARGIN = 40
    VERTICAL_OFFSET = 30

    def __init__(
        self, content: StampContent, font: pygame.font.Font, clock: Clock, *, placement: StampPlacement
    ) -> None:
        super().__init__(clock, self.DURATION)
        self._content = content
        self._font = font
        self._placement = placement

    def place(self, placement: StampPlacement) -> None:
        self._placement = placement

    def draw(self, surface: pygame.Surface) -> None:
        age = self.age
        box = self._tilted_box(age)
        if age > self.FADE_START:
            box.set_alpha(int(255 * (self.DURATION - age) / self.FADE_SECONDS))
        placement = self._placement
        half = box.get_width() // 2
        center_x = max(half, min(placement.screen_width - half, placement.center.x))
        surface.blit(box, box.get_rect(center=(center_x, placement.center.y + self.VERTICAL_OFFSET)))

    def _tilted_box(self, age: float) -> pygame.Surface:
        box = self._framed_message()
        growth = 1.0 + max(0.0, self.SLAM_SECONDS - age) * self.SLAM_GROWTH
        if growth > 1.01:
            return pygame.transform.rotozoom(box, self.TILT_DEGREES, growth)
        return pygame.transform.rotate(box, self.TILT_DEGREES)

    def _framed_message(self) -> pygame.Surface:
        color = self._content.color
        image = self._font.render(self._content.message, False, color)
        image = pygame.transform.scale_by(image, self._text_scale(image.get_width()))
        pad_x, pad_y = self.PADDING
        box = pygame.Surface((image.get_width() + pad_x, image.get_height() + pad_y), pygame.SRCALPHA)
        pygame.draw.rect(box, color, box.get_rect(), self.BORDER)
        box.blit(image, (pad_x // 2, pad_y // 2))
        return box

    def _text_scale(self, unscaled_width: int) -> int:
        scale = 2 if len(self._content.message) > self.LONG_MESSAGE_LENGTH else 3
        while scale > 1 and unscaled_width * scale + self.SCREEN_MARGIN > self._placement.screen_width:
            scale -= 1
        return scale
