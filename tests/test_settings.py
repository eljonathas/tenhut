import json

from tenhut.core import CameraCalibration, HeadPose, JudgePreference, MonitorSide, Settings, SettingsStore

LEGACY_CONFIG = {
    "trabalho_min": 50,
    "pausa_curta_min": 7,
    "pausa_longa_min": 20,
    "ciclos_ate_pausa_longa": 3,
    "juiz": "nenhum",
    "claude_bin": "claude",
    "modelo": "sonnet",
    "codex_bin": "codex",
    "modelo_codex": "",
    "espera_sem_juiz_seg": 30,
    "timeout_juiz_seg": 60,
    "max_minutos_liberacao": 10,
    "espera_apos_negacao_seg": 90,
    "idioma": "en",
    "som": False,
    "volume": 70,
    "notificacoes": False,
    "matar_apps": False,
    "camera": {
        "ativa": True,
        "dispositivo": 1,
        "monitor_da_camera": "DP-1",
        "tolerancia_seg": 9,
        "limiar_baixo_graus": 12,
        "limiar_lado_graus": 20,
        "minutos_penalidade": 2,
        "calibracao": {"base": [1, 2], "baixo": [1, -20], "lados": {"esquerda": [30, 0]}, "baixo_some": True},
    },
    "bloqueios": {
        "Esportes": {"dominios": ["ge.globo.com"], "apps": []},
        "Mine": {"dominios": ["example.com"], "apps": ["thing"]},
    },
}


def test_defaults_are_sane(cfg):
    assert (cfg.timer.work_minutes, cfg.timer.short_break_minutes, cfg.timer.long_break_minutes) == (25, 5, 15)
    assert cfg.timer.cycles_before_long_break == 4
    assert cfg.camera.enabled is False
    assert cfg.sound.volume == 40
    assert "YouTube" in cfg.block_list.names and "Sports" in cfg.block_list.names


def test_dict_round_trip_is_lossless(cfg):
    assert Settings.from_dict(cfg.to_dict()) == cfg
    assert list(cfg.to_dict()["camera"]) == [
        "enabled",
        "device",
        "camera_monitor",
        "tolerance_seconds",
        "down_threshold_degrees",
        "side_threshold_degrees",
        "penalty_minutes",
        "calibration",
    ]


def test_user_values_override_defaults_but_keep_new_keys(tmp_path):
    f = tmp_path / "config.json"
    f.write_text('{"work_minutes": 50, "camera": {"tolerance_seconds": 9}}')
    settings = SettingsStore(f).load()
    assert settings.timer.work_minutes == 50
    assert settings.camera.tolerance_seconds == 9 and settings.camera.enabled is False


def test_blocklist_from_the_user_replaces_the_default(tmp_path):
    f = tmp_path / "config.json"
    f.write_text('{"block_groups": {"Mine": {"domains": ["example.com"], "apps": []}}}')
    assert SettingsStore(f).load().block_list.names == ["Mine"]


def test_unknown_keys_are_ignored_and_bad_values_fall_back():
    settings = Settings.from_dict({"nonsense": 1, "work_minutes": "soon", "volume": 500, "judge": "gpt", "language": 3})
    assert settings.timer.work_minutes == 25
    assert settings.sound.volume == 100
    assert settings.judge.preference is JudgePreference.AUTO
    assert settings.language == "auto"


def test_out_of_range_values_are_clamped():
    settings = Settings.from_dict(
        {"work_minutes": 0, "cycles_before_long_break": 999, "camera": {"tolerance_seconds": -4}}
    )
    assert settings.timer.work_minutes == 1
    assert settings.timer.cycles_before_long_break == 24
    assert settings.camera.tolerance_seconds == 1


def test_corrupt_config_falls_back_to_defaults_and_is_left_alone(tmp_path):
    f = tmp_path / "config.json"
    f.write_text("{not json")
    assert SettingsStore(f).load().timer.work_minutes == 25
    assert f.read_text() == "{not json"


def test_missing_file_is_created_with_the_defaults(tmp_path):
    f = tmp_path / "sub" / "config.json"
    SettingsStore(f).load()
    assert json.loads(f.read_text())["work_minutes"] == 25


def test_legacy_portuguese_file_is_migrated_and_backed_up(tmp_path):
    f = tmp_path / "config.json"
    f.write_text(json.dumps(LEGACY_CONFIG))
    settings = SettingsStore(f).load()
    assert settings.timer.work_minutes == 50 and settings.timer.cycles_before_long_break == 3
    assert settings.judge.preference is JudgePreference.NONE
    assert settings.judge.claude_model == "sonnet" and settings.judge.timeout_seconds == 60
    assert settings.language == "en" and settings.sound.enabled is False
    assert settings.notifications_enabled is False and settings.close_blocked_apps is False
    assert settings.camera.camera_monitor == "DP-1" and settings.camera.penalty_minutes == 2
    assert settings.block_list.names == ["Sports", "Mine"]
    assert settings.block_list.apps_for({"Mine"}) == ["thing"]
    calibration = settings.camera.calibration
    assert calibration.sides == {MonitorSide.LEFT: HeadPose(30, 0)} and calibration.down_face_vanishes
    assert json.loads((tmp_path / "config.json.bak-pt").read_text()) == LEGACY_CONFIG
    rewritten = json.loads(f.read_text())
    assert "trabalho_min" not in rewritten and rewritten["work_minutes"] == 50
    assert rewritten["camera"]["calibration"]["sides"] == {"left": [30, 0]}


def test_migrated_file_is_not_migrated_twice(tmp_path):
    f = tmp_path / "config.json"
    f.write_text(json.dumps(LEGACY_CONFIG))
    store = SettingsStore(f)
    first = store.load()
    (tmp_path / "config.json.bak-pt").write_text("sentinel")
    assert store.load() == first
    assert (tmp_path / "config.json.bak-pt").read_text() == "sentinel"


def test_camera_calibration_dict_round_trip():
    calibration = CameraCalibration(HeadPose(1, 2), HeadPose(1, -20), {MonitorSide.RIGHT: HeadPose(-30, 1)})
    assert CameraCalibration.from_dict(calibration.to_dict()) == calibration
    assert CameraCalibration.from_dict({"base": [1, 2]}) is None


def test_with_camera_keeps_the_other_sections(cfg):
    calibration = CameraCalibration(HeadPose(0, 0), HeadPose(0, -20))
    updated = cfg.with_camera(cfg.camera.calibrated(calibration))
    assert updated.camera.enabled and updated.camera.is_ready()
    assert updated.timer == cfg.timer and cfg.camera.enabled is False
