from __future__ import annotations

import shutil

from .app_paths import APP_DIR, AppPaths


class LegacyDataMigration:
    """One-time moves of data written by earlier versions."""

    LEGACY_DIR = "general-foco"
    STATE_FILES = (("perfil.json", "profile.json"), ("pedidos.jsonl", "requests.jsonl"))

    def __init__(self, paths: AppPaths) -> None:
        self._paths = paths

    def run(self) -> list[str]:
        """Legacy folders first, then the renamed state files; returns what was moved."""
        return self.move_folders() + self.rename_state_files()

    def move_folders(self) -> list[str]:
        """Move `.../general-foco` to `.../tenhut`, only when the new folder does not exist.

        Never merges: if both exist the new one is the real one, and merging "newest wins" could
        overwrite a calibrated configuration with a default one.
        """
        moved = []
        for root in (self._paths.config_root, self._paths.state_root, self._paths.data_root):
            old, new = root / self.LEGACY_DIR, root / APP_DIR
            if old.is_dir() and not new.exists():
                try:
                    shutil.move(str(old), str(new))
                    moved.append(str(new))
                except OSError:
                    pass  # tried again on the next run
        return moved

    def rename_state_files(self) -> list[str]:
        renamed = []
        for old_name, new_name in self.STATE_FILES:
            old, new = self._paths.state_dir / old_name, self._paths.state_dir / new_name
            if old.is_file() and not new.exists():
                try:
                    old.rename(new)
                    renamed.append(str(new))
                except OSError:
                    pass
        return renamed
