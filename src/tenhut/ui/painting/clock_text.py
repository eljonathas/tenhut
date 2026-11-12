from __future__ import annotations


class ClockText:
    """Minutes and seconds as the board shows them."""

    SECONDS_PER_MINUTE = 60

    @classmethod
    def format(cls, seconds: float) -> str:
        whole = max(0, round(seconds))
        return f"{whole // cls.SECONDS_PER_MINUTE:02d}:{whole % cls.SECONDS_PER_MINUTE:02d}"
