from __future__ import annotations

from tenhut import i18n
from tenhut.controllers import ActiveSettings
from tenhut.core import RequestLog, SettingsStore, SystemClock
from tenhut.services.blocking import ProcessKiller, PsutilProcessSource
from tenhut.services.judge import JudgeFactory
from tenhut.services.platform import (
    AppPaths,
    LegacyDataMigration,
    NotifierFactory,
    OperatingSystem,
    SubprocessCommandRunner,
    SystemIntegration,
)
from tenhut.services.vision import MonitorLayout, MonitorProviderFactory

from .platform_parts import PlatformParts


class PlatformAssembly:
    """Detects the system, migrates old data and loads the settings."""

    @staticmethod
    def _load_settings(paths: AppPaths) -> tuple[SettingsStore, ActiveSettings]:
        LegacyDataMigration(paths).run()
        store = SettingsStore(paths.config_file)
        settings = ActiveSettings(store.load())
        i18n.set_language(settings.current.language)
        return store, settings

    def assemble(self) -> PlatformParts:
        system = OperatingSystem.current()
        clock = SystemClock()
        runner = SubprocessCommandRunner.for_system(system)
        paths = AppPaths.detect()
        store, settings = self._load_settings(paths)
        return PlatformParts(
            system=system,
            clock=clock,
            runner=runner,
            paths=paths,
            store=store,
            settings=settings,
            notifier=NotifierFactory.create(system, runner),
            integration=SystemIntegration(system, runner),
            judge_factory=JudgeFactory(runner, clock),
            monitors=MonitorLayout(MonitorProviderFactory.create(system, runner)),
            killer=ProcessKiller(PsutilProcessSource()),
            request_log=RequestLog(paths.request_log_file),
        )
