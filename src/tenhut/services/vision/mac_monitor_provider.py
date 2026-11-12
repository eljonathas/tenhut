from __future__ import annotations

import json

from ..platform import CommandError, CommandRunner, CommandSpec
from .monitor import Monitor
from .monitor_provider import MonitorProvider


class MacMonitorProvider(MonitorProvider):
    """Monitors from NSScreen, read through osascript."""

    SCREENS_SCRIPT = (
        "ObjC.import('AppKit');var o=[],s=$.NSScreen.screens;"
        "for(var i=0;i<s.count;i++){var sc=s.objectAtIndex(i),f=sc.frame,n='';"
        "try{n=ObjC.unwrap(sc.localizedName)}catch(e){}"
        "o.push({name:n,x:f.origin.x,y:f.origin.y,w:f.size.width,h:f.size.height})}"
        "JSON.stringify(o)"
    )

    def __init__(self, runner: CommandRunner) -> None:
        self._runner = runner

    @classmethod
    def parse(cls, text: str) -> list[Monitor]:
        """Monitors from the JSON of `osascript -l JavaScript` ([{x,y,w,h,name?}, ...] of NSScreen.screens).

        osascript may mix warnings into the output, so the whole text is tried first, then each line starting with "[".
        """
        for candidate in [text.strip(), *(ln.strip() for ln in text.splitlines() if ln.strip().startswith("["))]:
            monitors = cls._from_json(candidate)
            if monitors:
                return monitors
        return []

    @staticmethod
    def _from_json(raw: str) -> list[Monitor]:
        """The first NSScreen is the main one; the y axis grows upward, so it is flipped to "top = 0"."""
        try:
            screens = json.loads(raw)
            top_reference = int(float(screens[0]["y"]) + float(screens[0]["h"])) if screens else 0
            monitors = []
            for index, screen in enumerate(screens):
                height = int(float(screen["h"]))
                monitors.append(
                    Monitor(
                        str(screen.get("name") or f"Display {index + 1}"),
                        int(float(screen["x"])),
                        top_reference - (int(float(screen["y"])) + height),
                        int(float(screen["w"])),
                        height,
                        index == 0,
                    )
                )
            return monitors
        except (ValueError, KeyError, TypeError, IndexError, AttributeError):
            return []

    def list_monitors(self) -> list[Monitor]:
        spec = CommandSpec(("osascript", "-l", "JavaScript", "-e", self.SCREENS_SCRIPT), timeout=8)
        try:
            result = self._runner.run(spec)
        except CommandError:
            return []
        # osascript writes the JXA result to stdout or stderr depending on the version
        return self.parse(result.stdout) or self.parse(result.stderr)
