from __future__ import annotations

from .monitor import Monitor
from .monitor_provider import MonitorProvider
from .screen_rect import ScreenRect


class WindowsMonitorProvider(MonitorProvider):
    """Monitors from the Win32 API."""

    PRIMARY_FLAG = 1

    @classmethod
    def monitor_from_info(cls, device: str, rect: ScreenRect, flags: int) -> Monitor:
        """A Monitor from a MONITORINFOEXW (rectangle in pixels)."""
        return Monitor(
            device or "?",
            rect.left,
            rect.top,
            rect.right - rect.left,
            rect.bottom - rect.top,
            bool(flags & cls.PRIMARY_FLAG),
        )

    def list_monitors(self) -> list[Monitor]:
        try:
            return self._enumerate()
        except (AttributeError, OSError, ImportError):
            return []

    @staticmethod
    def _info_structure():
        import ctypes
        from ctypes import wintypes

        class MonitorInfo(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT),
                ("dwFlags", wintypes.DWORD),
                ("szDevice", wintypes.WCHAR * 32),
            ]

        return MonitorInfo

    def _enumerate(self) -> list[Monitor]:
        import ctypes
        from ctypes import wintypes

        info_type = self._info_structure()
        found: list[Monitor] = []
        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(info_type)]

        def on_monitor(handle, _dc, _rect, _data) -> int:
            info = info_type()
            info.cbSize = ctypes.sizeof(info_type)
            if user32.GetMonitorInfoW(handle, ctypes.byref(info)):
                r = info.rcMonitor
                found.append(
                    self.monitor_from_info(info.szDevice, ScreenRect(r.left, r.top, r.right, r.bottom), info.dwFlags)
                )
            return 1

        callback_type = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(wintypes.RECT), ctypes.c_void_p
        )
        user32.EnumDisplayMonitors(None, None, callback_type(on_monitor), 0)
        return found
