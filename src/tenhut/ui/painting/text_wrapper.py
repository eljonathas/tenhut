from __future__ import annotations

import pygame


class TextWrapper:
    """Breaks text into lines that fit a pixel width."""

    def __init__(self, font: pygame.font.Font) -> None:
        self._font = font

    def lines(self, text: str, width: int) -> list[str]:
        """Word wrap; a word wider than the line is broken by force."""
        return [line for paragraph in text.split("\n") for line in self._paragraph(paragraph, width)]

    def _paragraph(self, paragraph: str, width: int) -> list[str]:
        lines: list[str] = []
        current = ""
        for word in paragraph.split(" "):
            candidate = (current + " " + word).strip() if current else word
            if self._width(candidate) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = self._break_oversized(word, width, lines)
        lines.append(current)
        return lines

    def _break_oversized(self, word: str, width: int, lines: list[str]) -> str:
        while self._width(word) > width:
            end = len(word)
            while end > 1 and self._width(word[:end]) > width:
                end -= 1
            lines.append(word[:end])
            word = word[end:]
        return word

    def _width(self, text: str) -> int:
        return self._font.size(text)[0]
