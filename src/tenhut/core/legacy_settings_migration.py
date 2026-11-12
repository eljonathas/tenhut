from __future__ import annotations

from typing import ClassVar


class LegacySettingsMigration:
    """Converts a config file written with the old Portuguese keys to the English schema."""

    TOP_LEVEL_KEYS: ClassVar[dict[str, str]] = {
        "trabalho_min": "work_minutes",
        "pausa_curta_min": "short_break_minutes",
        "pausa_longa_min": "long_break_minutes",
        "ciclos_ate_pausa_longa": "cycles_before_long_break",
        "juiz": "judge",
        "claude_bin": "claude_binary",
        "modelo": "claude_model",
        "codex_bin": "codex_binary",
        "modelo_codex": "codex_model",
        "espera_sem_juiz_seg": "local_wait_seconds",
        "timeout_juiz_seg": "judge_timeout_seconds",
        "max_minutos_liberacao": "max_grant_minutes",
        "espera_apos_negacao_seg": "denial_cooldown_seconds",
        "idioma": "language",
        "som": "sound_enabled",
        "notificacoes": "notifications_enabled",
        "matar_apps": "close_blocked_apps",
        "bloqueios": "block_groups",
    }
    CAMERA_KEYS: ClassVar[dict[str, str]] = {
        "ativa": "enabled",
        "dispositivo": "device",
        "monitor_da_camera": "camera_monitor",
        "tolerancia_seg": "tolerance_seconds",
        "limiar_baixo_graus": "down_threshold_degrees",
        "limiar_lado_graus": "side_threshold_degrees",
        "minutos_penalidade": "penalty_minutes",
        "calibracao": "calibration",
    }
    CALIBRATION_KEYS: ClassVar[dict[str, str]] = {"baixo": "down", "lados": "sides", "baixo_some": "down_face_vanishes"}
    JUDGE_VALUES: ClassVar[dict[str, str]] = {"nenhum": "none"}
    GROUP_NAMES: ClassVar[dict[str, str]] = {"Esportes": "Sports"}
    SIDE_NAMES: ClassVar[dict[str, str]] = {"esquerda": "left", "direita": "right"}

    def is_legacy(self, raw: dict[str, object]) -> bool:
        camera = raw.get("camera")
        has_old_camera = isinstance(camera, dict) and bool(self.CAMERA_KEYS.keys() & camera.keys())
        return bool(self.TOP_LEVEL_KEYS.keys() & raw.keys()) or has_old_camera

    def migrate(self, raw: dict[str, object]) -> dict[str, object]:
        """An English key already present wins over its Portuguese twin."""
        out = self._rename(raw, self.TOP_LEVEL_KEYS)
        if out.get("judge") in self.JUDGE_VALUES:
            out["judge"] = self.JUDGE_VALUES[str(out["judge"])]
        if isinstance(out.get("camera"), dict):
            out["camera"] = self._migrate_camera(out["camera"])
        if isinstance(out.get("block_groups"), dict):
            out["block_groups"] = self._migrate_groups(out["block_groups"])
        return out

    @staticmethod
    def _rename(data: dict[str, object], names: dict[str, str]) -> dict[str, object]:
        out = {k: v for k, v in data.items() if k not in names}
        for old, new in names.items():
            if old in data and new not in out:
                out[new] = data[old]
        return out

    def _migrate_camera(self, camera: dict[str, object]) -> dict[str, object]:
        out = self._rename(camera, self.CAMERA_KEYS)
        calibration = out.get("calibration")
        if isinstance(calibration, dict):
            migrated = self._rename(calibration, self.CALIBRATION_KEYS)
            sides = migrated.get("sides")
            if isinstance(sides, dict):
                migrated["sides"] = self._rename(sides, self.SIDE_NAMES)
            out["calibration"] = migrated
        return out

    def _migrate_groups(self, groups: dict[str, object]) -> dict[str, object]:
        return {self.GROUP_NAMES.get(name, name): self._migrate_group(group) for name, group in groups.items()}

    def _migrate_group(self, group: object) -> object:
        return self._rename(group, {"dominios": "domains"}) if isinstance(group, dict) else group
