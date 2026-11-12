from __future__ import annotations

import contextlib
import shutil
import sys
from pathlib import Path

from ...asset_paths import AssetPaths
from .command_error import CommandError
from .command_runner import CommandRunner
from .command_spec import CommandSpec
from .desktop_integration import APP_ID, APP_NAME, DesktopIntegration


class LinuxDesktop(DesktopIntegration):
    """Freedesktop launcher (.desktop) and hicolor icons in the user's data folder."""

    supported = True
    ICON_SIZES = (16, 24, 32, 48, 64, 128, 256, 512)
    OLD_IDS = ("general-foco",)

    def __init__(self, data_home: Path, runner: CommandRunner) -> None:
        super().__init__()
        self._apps_dir = data_home / "applications"
        self._icons_dir = data_home / "icons" / "hicolor"
        self._runner = runner

    @staticmethod
    def exec_line() -> str:
        script = Path(sys.prefix) / "bin" / APP_ID
        if script.exists():
            return str(script)
        uv = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
        project = Path(__file__).resolve().parents[4]
        return f"{uv} run --project {project} {APP_ID}"

    def desktop_entry(self) -> str:
        return f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
GenericName=Focus Timer
GenericName[pt_BR]=Temporizador de foco
Comment=Aggressive pomodoro: a pixel-art general blocks distractions until your mission is done
Comment[pt_BR]=Pomodoro agressivo: um general em pixel art bloqueia distrações até a missão acabar
Exec={self.exec_line()}
Icon={APP_ID}
Terminal=false
Categories=Utility;
Keywords=focus;pomodoro;productivity;blocker;foco;produtividade;
StartupNotify=true
StartupWMClass={APP_ID}
"""

    def install(self) -> list[Path]:
        written = self._install_icons()
        self._apps_dir.mkdir(parents=True, exist_ok=True)
        entry = self._apps_dir / f"{APP_ID}.desktop"
        entry.write_text(self.desktop_entry())
        for old in self.OLD_IDS:
            (self._apps_dir / f"{old}.desktop").unlink(missing_ok=True)
        self._refresh_caches()
        return [*written, entry]

    def uninstall(self) -> None:
        for size in self.ICON_SIZES:
            self._icon_target(size).unlink(missing_ok=True)
        for app_id in (APP_ID, *self.OLD_IDS):
            (self._apps_dir / f"{app_id}.desktop").unlink(missing_ok=True)
        self._refresh_caches()

    def _icon_target(self, size: int) -> Path:
        return self._icons_dir / f"{size}x{size}" / "apps" / f"{APP_ID}.png"

    def _install_icons(self) -> list[Path]:
        written = []
        for size in self.ICON_SIZES:
            target = self._icon_target(size)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(AssetPaths.icons_dir() / f"icon-{size}.png", target)
            written.append(target)
        return written

    def _refresh_caches(self) -> None:
        commands = (
            ("gtk-update-icon-cache", "-f", "-t", str(self._icons_dir)),
            ("update-desktop-database", str(self._apps_dir)),
        )
        for argv in commands:
            if shutil.which(argv[0]):
                with contextlib.suppress(CommandError):
                    self._runner.run(CommandSpec(argv))
