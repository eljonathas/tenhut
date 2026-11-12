from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from ...i18n import t
from .helper_error import HelperError
from .helper_scripts import HelperScripts


class HelperLocator:
    """Finds the `hosts-helper` file: the installed copy and the one bundled with the package."""

    def __init__(self) -> None:
        self._module: ModuleType | None = None

    @staticmethod
    def installed_path() -> str:
        """The new helper when installed, else the old one (until install.sh runs again)."""
        if Path(HelperScripts.HELPER_DEST).exists() or not Path(HelperScripts.OLD_HELPER_DEST).exists():
            return HelperScripts.HELPER_DEST
        return HelperScripts.OLD_HELPER_DEST

    @staticmethod
    def candidates() -> list[Path]:
        here = Path(__file__).resolve().parent
        found: list[Path] = []
        bundle = getattr(sys, "_MEIPASS", None)
        if bundle:
            found.append(Path(bundle) / "helper" / "hosts-helper")
        found += [
            here.parents[3] / "helper" / "hosts-helper",
            here.parents[1] / "helper" / "hosts-helper",
            Path(sys.executable).resolve().parent / "helper" / "hosts-helper",
        ]
        return found

    def bundled(self) -> Path | None:
        for candidate in self.candidates():
            try:
                if candidate.is_file():
                    return candidate
            except OSError:
                continue
        return None

    def load_module(self, path: Path | None = None) -> ModuleType:
        """Load the helper file as a module (Windows writes the hosts file in-process with it)."""
        if path is None and self._module is not None:
            return self._module
        source = path or self.bundled()
        if source is None:
            raise HelperError(t("error.helper.file_missing"))
        loader = importlib.machinery.SourceFileLoader("tenhut_hosts_helper", str(source))
        spec = importlib.util.spec_from_loader("tenhut_hosts_helper", loader)
        if spec is None:
            raise HelperError(str(source))
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        if path is None:
            self._module = module
        return module
