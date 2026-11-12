"""Blocking distractions: the hosts file (async Blocker + a backend per OS) and the blocked apps."""

from .blocker import Blocker
from .dry_run_backend import DryRunBackend
from .hosts_backend import HostsBackend
from .hosts_backend_factory import HostsBackendFactory
from .hosts_error import HostsError
from .install_hint import InstallHint
from .posix_helper_backend import PosixHelperBackend
from .process_killer import ProcessKiller
from .process_source import ProcessSource
from .psutil_process_source import PsutilProcessSource
from .running_process import RunningProcess
from .windows_direct_backend import WindowsDirectBackend

__all__ = [
    "Blocker",
    "DryRunBackend",
    "HostsBackend",
    "HostsBackendFactory",
    "HostsError",
    "InstallHint",
    "PosixHelperBackend",
    "ProcessKiller",
    "ProcessSource",
    "PsutilProcessSource",
    "RunningProcess",
    "WindowsDirectBackend",
]
