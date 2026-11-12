from __future__ import annotations


class AppleScript:
    """Helpers for building AppleScript source safely."""

    @staticmethod
    def quote(text: str) -> str:
        """A string literal (newlines become spaces)."""
        escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\r", " ").replace("\n", " ")
        return f'"{escaped}"'
