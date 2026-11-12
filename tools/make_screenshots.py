"""Renders the README screenshots into docs/screenshots (English UI, 1120x720 window).

    uv run python tools/make_screenshots.py

Runs headless with throw-away data folders and a fake clock, so the output is reproducible and your
real settings are never touched.
"""

from __future__ import annotations

import os
import random
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
SANDBOX = tempfile.mkdtemp(prefix="tenhut-shots-")
os.environ.update(
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    XDG_CONFIG_HOME=f"{SANDBOX}/config",
    XDG_STATE_HOME=f"{SANDBOX}/state",
    XDG_DATA_HOME=f"{SANDBOX}/data",
)

import pygame  # noqa: E402

from tenhut import i18n  # noqa: E402
from tenhut.application import Application  # noqa: E402
from tenhut.application_options import ApplicationOptions  # noqa: E402
from tenhut.controllers import PageId  # noqa: E402

TASKS = ("Write the release notes", "Review the open pull requests", "Fix the flaky test", "Ship version 0.2")
FRAME_SECONDS = 1 / 30


class ScreenshotSession:
    """Drives a scripted mission with a fake clock and saves the interesting frames."""

    def __init__(self) -> None:
        self._now = 1_800_000_000.0
        time.time = lambda: self._now
        real_localtime = time.localtime
        time.localtime = lambda secs=None: real_localtime(self._now if secs is None else secs)
        pygame.time.get_ticks = lambda: int((self._now % 100000) * 1000)
        random.seed(2026)
        self._app = Application(ApplicationOptions(dry_run=True, headless=True))
        self._controllers = self._app.parts.controllers
        self._navigator = self._controllers.navigator
        i18n.set_language("en")
        self._navigator.open(PageId.MAIN)

    def run(self, frames: int) -> None:
        for _ in range(frames):
            self._now += FRAME_SECONDS
            for event in pygame.event.get():
                self._app.handle(event)
            self._app.tick(FRAME_SECONDS)
            self._app.draw()

    def quiet(self) -> None:
        self._app.parts.world.balloon.silence()
        self._controllers.speech.release_reaction()

    def save(self, name: str) -> None:
        OUT.mkdir(parents=True, exist_ok=True)
        pygame.image.save(self._app.parts.world.window.surface, OUT / f"{name}.png")
        print("saved", OUT / f"{name}.png")

    def start_mission(self) -> None:
        self._controllers.mission.new_mission()
        for task in TASKS:
            self._navigator.current.inputs[0].text = task
            self._navigator.current.add_task()
        self._controllers.mission.start_mission()

    def complete_task(self, index: int, settle_frames: int = 80) -> None:
        self._controllers.mission.toggle_task(index)
        self.run(settle_frames)
        self.quiet()

    def script(self) -> None:
        self.run(30)
        self.start_mission()
        self.run(90)
        self.quiet()
        self.run(5)
        self.save("office")
        self._controllers.gestures.poke(2)
        self.run(11)
        self.save("poke")
        self.run(40)
        self.complete_task(0)
        self.save("field")
        self.complete_task(1)
        self.save("trench")
        self._navigator.open(PageId.SETTINGS)
        self.run(5)
        self.save("settings")
        self._navigator.open(PageId.MAIN)
        self.complete_task(2)
        self._controllers.mission.toggle_task(3)
        self.run(220)
        self.save("parade")


if __name__ == "__main__":
    ScreenshotSession().script()
