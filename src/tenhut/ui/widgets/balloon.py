from __future__ import annotations

from collections import deque

import pygame

from tenhut.game.audio import SoundBank, SoundEffect
from tenhut.game.geometry import Point
from tenhut.ui.painting import TextStyle, TextWrapper, UiCanvas, UiPalette

from .balloon_line import BalloonLine


class Balloon:
    """The general's speech balloon: typewriter text, a queue of lines and a tail pointing at his mouth."""

    TYPING_SPEED = 48
    BASE_HOLD = 2.5
    CHARACTERS_PER_SECOND_OF_HOLD = 18
    BLIP_EVERY = 2
    MAX_WIDTH = 250
    TEXT_MARGIN = 16
    WIDTH_PADDING = 18
    LINE_HEIGHT = 13
    HEIGHT_PADDING = 12
    TAIL_GAP = 10
    SHADOW_OFFSET = 2
    BEVEL = 4
    EDGE = 2
    FILL_TRIM = 6
    TAIL_BASE_RISE = 2
    TAIL_TIP = (2, 8)
    TAIL_WIDTH = 10
    TAIL_OUTLINE = 2
    TAIL_ANCHOR_DIVISOR = 3
    MARKER = ((-12, -9), (-6, -9), (-9, -6))
    TEXT_INSET = (9, 6)
    TAIL_MIN_INSET = 10
    TAIL_MAX_INSET = 14
    MARKER_BLINK_MS = 300

    def __init__(self, sounds: SoundBank) -> None:
        self._sounds = sounds
        self._queue: deque[BalloonLine] = deque()
        self._current: BalloonLine | None = None
        self._shown = 0.0
        self._hold = 0.0
        self._persist = False

    @property
    def text(self) -> str | None:
        return self._current.message if self._current else None

    @property
    def typing(self) -> bool:
        return self._current is not None and self._shown < len(self._current.message)

    @property
    def visible(self) -> bool:
        return self._current is not None

    def say(self, message: str, *, hold: float | None = None, interrupt: bool = True, persist: bool = False) -> None:
        if interrupt:
            self.silence()
        self._queue.append(BalloonLine(message, hold if hold is not None else self._default_hold(message)))
        self._persist = persist

    def silence(self) -> None:
        """Drops the line being said and every queued one."""
        self._queue.clear()
        self._current = None

    def skip(self) -> None:
        """Finishes typing the line; once typed, dismisses it."""
        if self._current is None:
            return
        if self.typing:
            self._shown = len(self._current.message)
        else:
            self._hold = 0
            self._persist = False

    def update(self, dt: float) -> None:
        if self._current is None and self._queue:
            self._current = self._queue.popleft()
            self._shown, self._hold = 0.0, self._current.hold
        if self._current is None:
            return
        if self.typing:
            self._type(dt)
        elif not (self._persist and not self._queue):
            self._hold -= dt
            if self._hold <= 0:
                self._current = None

    def draw(self, canvas: UiCanvas, anchor: Point, area: pygame.Rect) -> None:
        if self._current is None:
            return
        font = canvas.fonts.body
        max_width = min(area.w, self.MAX_WIDTH)
        lines = TextWrapper(font).lines(self._current.message, max_width - self.TEXT_MARGIN)
        width = min(max_width, max(font.size(line)[0] for line in lines) + self.WIDTH_PADDING)
        height = len(lines) * self.LINE_HEIGHT + self.HEIGHT_PADDING
        left = max(area.x, min(anchor.x - width // self.TAIL_ANCHOR_DIVISOR, area.right - width))
        bubble = pygame.Rect(left, anchor.y - height - self.TAIL_GAP, width, height)
        self._draw_body(canvas, bubble)
        self._draw_tail(canvas, bubble, anchor)
        self._draw_text(canvas, bubble, lines)
        self._draw_continue_marker(canvas, bubble)

    @classmethod
    def _default_hold(cls, message: str) -> float:
        return cls.BASE_HOLD + len(message) / cls.CHARACTERS_PER_SECOND_OF_HOLD

    def _type(self, dt: float) -> None:
        assert self._current is not None
        before = int(self._shown)
        self._shown = min(len(self._current.message), self._shown + dt * self.TYPING_SPEED)
        blip = int(self._shown) // self.BLIP_EVERY != before // self.BLIP_EVERY
        if blip and self._current.message[before : before + 1].strip():
            self._sounds.play(SoundEffect.BLIP)

    def _draw_body(self, canvas: UiCanvas, bubble: pygame.Rect) -> None:
        shapes = canvas.shapes
        shadow = bubble.move(self.SHADOW_OFFSET, self.SHADOW_OFFSET)
        for area, color in ((shadow, UiPalette.SHADOW), (bubble, UiPalette.INK)):
            shapes.rect(color, area.inflate(0, -self.BEVEL))
            shapes.rect(color, area.inflate(-self.BEVEL, 0))
            shapes.rect(color, area.inflate(-self.EDGE, -self.EDGE))
        shapes.rect(UiPalette.PAPER, bubble.inflate(-self.BEVEL, -self.FILL_TRIM))
        shapes.rect(UiPalette.PAPER, bubble.inflate(-self.FILL_TRIM, -self.BEVEL))

    def _draw_tail(self, canvas: UiCanvas, bubble: pygame.Rect, anchor: Point) -> None:
        left = max(bubble.x + self.TAIL_MIN_INSET, min(anchor.x, bubble.right - self.TAIL_MAX_INSET))
        base = bubble.bottom - self.TAIL_BASE_RISE
        tip = (left + self.TAIL_TIP[0], bubble.bottom + self.TAIL_TIP[1])
        grow = self.TAIL_OUTLINE
        outline = [(left - grow, base), (left + self.TAIL_WIDTH + grow, base), (tip[0] - 1, tip[1] + grow)]
        canvas.shapes.polygon(UiPalette.INK, outline)
        canvas.shapes.polygon(UiPalette.PAPER, [(left, base), (left + self.TAIL_WIDTH, base), tip])

    def _draw_text(self, canvas: UiCanvas, bubble: pygame.Rect, lines: list[str]) -> None:
        style = TextStyle(canvas.fonts.body, UiPalette.INK)
        typed = int(self._shown)
        inset_x, inset_y = self.TEXT_INSET
        for index, line in enumerate(lines):
            if typed <= 0:
                break
            canvas.write(line[:typed], Point(bubble.x + inset_x, bubble.y + inset_y + index * self.LINE_HEIGHT), style)
            typed -= len(line) + 1

    def _draw_continue_marker(self, canvas: UiCanvas, bubble: pygame.Rect) -> None:
        if self.typing or not (self._queue or self._persist):
            return
        if int(pygame.time.get_ticks() / self.MARKER_BLINK_MS) % 2:
            points = [(bubble.right + dx, bubble.bottom + dy) for dx, dy in self.MARKER]
            canvas.shapes.polygon(UiPalette.INK, points)
