from __future__ import annotations


class SettingValue:
    """Turns untrusted JSON values into typed setting values; a wrong type falls back to the default."""

    @staticmethod
    def flag(value: object, default: bool) -> bool:
        return value if isinstance(value, bool) else default

    @staticmethod
    def text(value: object, default: str) -> str:
        return value if isinstance(value, str) else default

    @staticmethod
    def texts(value: object) -> tuple[str, ...]:
        return tuple(v for v in value if isinstance(v, str)) if isinstance(value, list) else ()
