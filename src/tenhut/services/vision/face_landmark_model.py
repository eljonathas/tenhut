from __future__ import annotations

import urllib.request
from pathlib import Path


class FaceLandmarkModel:
    """The MediaPipe face-landmarker file, downloaded on first use."""

    URL = (
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    )
    MIN_BYTES = 1_000_000

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def ensure(self) -> None:
        if self._path.exists() and self._path.stat().st_size > self.MIN_BYTES:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        partial = self._path.with_suffix(".part")
        urllib.request.urlretrieve(self.URL, partial)
        partial.replace(self._path)
