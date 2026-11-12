from __future__ import annotations

from dataclasses import dataclass

from tenhut.controllers import ActiveSettings
from tenhut.core import Clock, RequestLog, SettingsStore
from tenhut.services.blocking import ProcessKiller
from tenhut.services.judge import JudgeFactory
from tenhut.services.platform import AppPaths, CommandRunner, Notifier, OperatingSystem, SystemIntegration
from tenhut.services.vision import MonitorLayout


@dataclass(frozen=True, slots=True)
class PlatformParts:
    """The services that talk to the operating system and the user's files."""

    system: OperatingSystem
    clock: Clock
    runner: CommandRunner
    paths: AppPaths
    store: SettingsStore
    settings: ActiveSettings
    notifier: Notifier
    integration: SystemIntegration
    judge_factory: JudgeFactory
    monitors: MonitorLayout
    killer: ProcessKiller
    request_log: RequestLog
