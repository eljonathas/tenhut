from __future__ import annotations

from .elevator import Elevator
from .no_elevator import NoElevator
from .operating_system import OperatingSystem
from .osascript_elevator import OsascriptElevator
from .pkexec_elevator import PkexecElevator
from .root_elevator import RootElevator


class ElevatorFactory:
    """Picks the elevation strategy for the OS."""

    @staticmethod
    def create(system: OperatingSystem, is_root: bool) -> Elevator:
        if system.is_windows:
            return NoElevator()
        if is_root:
            return RootElevator()
        return OsascriptElevator() if system.is_mac else PkexecElevator()
