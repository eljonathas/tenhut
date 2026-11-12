from __future__ import annotations

from tenhut.controllers.active_settings import ActiveSettings
from tenhut.core import Clock
from tenhut.services.platform import AppPaths, OperatingSystem
from tenhut.services.vision import CameraWatcher, FaceLandmarkModel

from .camera_stop_listener import CameraStopListener
from .gaze_status import GazeStatus


class CameraHolder:
    """Owns the camera thread: starts it, stops it in the background and keeps the current reading."""

    JOIN_TIMEOUT = 2

    def __init__(self, settings: ActiveSettings, paths: AppPaths, clock: Clock, *, system: OperatingSystem) -> None:
        self._settings = settings
        self._paths = paths
        self._clock = clock
        self._system = system
        self._watcher: CameraWatcher | None = None
        self._stopping: CameraWatcher | None = None
        self._status = GazeStatus.none()
        self._listeners: list[CameraStopListener] = []

    @property
    def watcher(self) -> CameraWatcher | None:
        return self._watcher

    @property
    def status(self) -> GazeStatus:
        return self._status

    @status.setter
    def status(self, status: GazeStatus) -> None:
        self._status = status

    def subscribe(self, listener: CameraStopListener) -> None:
        self._listeners.append(listener)

    def ensure(self, wanted: bool) -> None:
        if wanted and self._watcher is None:
            self._start()
        elif not wanted and self._watcher is not None:
            self._stop()

    def shutdown(self) -> None:
        """On exit the thread is waited for (MediaPipe aborts otherwise)."""
        self.ensure(False)
        if self._stopping:
            self._stopping.join(timeout=self.JOIN_TIMEOUT)

    def _start(self) -> None:
        previous = self._stopping if self._stopping and self._stopping.is_alive() else None
        model = FaceLandmarkModel(self._paths.camera_model_file)
        self._watcher = CameraWatcher(
            self._settings.current.camera.device, model, self._clock, system=self._system, wait_for=previous
        )
        self._watcher.start()

    def _stop(self) -> None:
        # stopping in the background: waiting here froze the interface (for instance on victory)
        self._watcher.stop()
        self._stopping, self._watcher = self._watcher, None
        self._status = GazeStatus.none()
        for listener in self._listeners:
            listener.camera_stopped()
