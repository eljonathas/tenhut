"""Tenhut: an aggressive pomodoro with a pixel-art general watching you."""


def main() -> None:
    """Entry point of the ``tenhut`` command."""
    from .cli import CommandLine

    raise SystemExit(CommandLine().command().run())
