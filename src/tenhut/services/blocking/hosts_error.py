from __future__ import annotations

from ...core import TenhutError


class HostsError(TenhutError):
    """Writing the hosts file failed; the message is short and fit for the interface."""
