from pathlib import Path

from tenhut.services.platform import AppPaths, LegacyDataMigration


def make_paths(tmp_path):
    roots = [tmp_path / n for n in ("config", "state", "data")]
    for r in roots:
        r.mkdir()
    return AppPaths(*roots)


def test_legacy_folders_are_moved_when_the_new_one_is_missing(tmp_path):
    paths = make_paths(tmp_path)
    (paths.config_root / "general-foco").mkdir()
    (paths.config_root / "general-foco" / "config.json").write_text("{}")
    (paths.state_root / "general-foco").mkdir()
    (paths.state_root / "general-foco" / "state.json").write_text("{}")
    assert len(LegacyDataMigration(paths).move_folders()) == 2
    assert paths.config_file.exists() and not (paths.config_root / "general-foco").exists()


def test_migration_never_overwrites_an_existing_new_folder(tmp_path):
    paths = make_paths(tmp_path)
    paths.config_dir.mkdir()
    paths.config_file.write_text('{"work_minutes": 40}')
    (paths.config_root / "general-foco").mkdir()
    (paths.config_root / "general-foco" / "config.json").write_text('{"work_minutes": 25}')
    assert LegacyDataMigration(paths).move_folders() == []
    assert '"work_minutes": 40' in paths.config_file.read_text()
    assert (paths.config_root / "general-foco" / "config.json").exists()


def test_state_files_are_renamed_only_when_the_new_one_is_absent(tmp_path):
    paths = make_paths(tmp_path)
    paths.state_dir.mkdir()
    (paths.state_dir / "perfil.json").write_text("old")
    (paths.state_dir / "pedidos.jsonl").write_text("old")
    paths.request_log_file.write_text("new")
    renamed = LegacyDataMigration(paths).rename_state_files()
    assert renamed == [str(paths.profile_file)]
    assert paths.profile_file.read_text() == "old" and paths.request_log_file.read_text() == "new"
    assert (paths.state_dir / "pedidos.jsonl").exists()


def test_xdg_variables_win_on_every_os(tmp_path):
    env = {"XDG_CONFIG_HOME": str(tmp_path / "c"), "XDG_STATE_HOME": "", "APPDATA": str(tmp_path / "ra")}
    home = Path("/home/u")
    windows = AppPaths.detect("win32", env, home)
    assert windows.config_root == tmp_path / "c"
    assert windows.state_root == home / "AppData" / "Local"


def test_default_roots_per_os():
    home = Path("/home/u")
    assert AppPaths.detect("linux", {}, home).state_root == home / ".local" / "state"
    mac = AppPaths.detect("darwin", {}, home)
    assert mac.data_root == home / "Library" / "Application Support"
