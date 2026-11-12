from __future__ import annotations

from dataclasses import dataclass

from .ambient_controllers import AmbientControllers
from .camera_controllers import CameraControllers
from .core_controllers import CoreControllers
from .rule_controllers import RuleControllers


@dataclass(frozen=True, slots=True)
class ControllerGroups:
    """The groups of controllers built so far."""

    core: CoreControllers
    rules: RuleControllers
    camera: CameraControllers
    ambient: AmbientControllers
