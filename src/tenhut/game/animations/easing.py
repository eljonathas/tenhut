from __future__ import annotations


class Easing:
    """Maps linear progress to eased progress."""

    @staticmethod
    def out_cubic(progress: float) -> float:
        """Fast start, soft landing; progress is clamped to 0..1."""
        progress = max(0.0, min(1.0, progress))
        return 1 - (1 - progress) ** 3
