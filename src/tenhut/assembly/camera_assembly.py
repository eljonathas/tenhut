from __future__ import annotations

from tenhut.controllers import CalibrationController, CameraController, CameraHolder

from .camera_controllers import CameraControllers
from .core_controllers import CoreControllers
from .platform_parts import PlatformParts
from .world_parts import WorldParts


class CameraAssembly:
    """Creates the camera holder, the posture watcher and the calibration."""

    def __init__(self, platform: PlatformParts, world: WorldParts, core: CoreControllers) -> None:
        self._platform = platform
        self._world = world
        self._core = core

    def assemble(self) -> CameraControllers:
        holder = CameraHolder(
            self._platform.settings, self._platform.paths, self._platform.clock, system=self._platform.system
        )
        camera = self._camera(holder)
        holder.subscribe(camera)
        return CameraControllers(holder, camera, self._calibration(holder))

    def _camera(self, holder: CameraHolder) -> CameraController:
        platform, world, core = self._platform, self._world, self._core
        return CameraController(
            holder=holder,
            session=world.session,
            settings=platform.settings,
            clock=platform.clock,
            navigation=core.navigator,
            speech=core.speech,
            feedback=core.feedback,
            gestures=core.gestures,
            general=world.general,
            randomness=world.randomness,
        )

    def _calibration(self, holder: CameraHolder) -> CalibrationController:
        platform, world, core = self._platform, self._world, self._core
        return CalibrationController(
            holder=holder,
            monitors=platform.monitors,
            settings=platform.settings,
            store=platform.store,
            clock=platform.clock,
            navigation=core.navigator,
            speech=core.speech,
            feedback=core.feedback,
            general=world.general,
        )
