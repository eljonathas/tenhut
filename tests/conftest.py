"""Test setup: headless SDL and throw-away data folders, applied BEFORE tenhut is imported.

Detecting the app paths reads the user's config/state/data folders, so every test run points the
XDG_* variables (honoured on every OS) at a temporary directory.
"""

import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="tenhut-tests-"))
for _var, _sub in (("XDG_CONFIG_HOME", "config"), ("XDG_STATE_HOME", "state"), ("XDG_DATA_HOME", "data")):
    os.environ[_var] = str(_TMP / _sub)
# Pin the locale so "auto" resolves to the same language on every machine and CI runner.
for _var in ("LC_ALL", "LC_MESSAGES", "LANGUAGE"):
    os.environ.pop(_var, None)
os.environ["LANG"] = "pt_BR.UTF-8"
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pytest  # noqa: E402

from tenhut import i18n  # noqa: E402


@pytest.fixture(autouse=True)
def _portuguese_ui():
    """The source language is Portuguese; tests assume it unless they switch explicitly."""
    i18n.set_language("pt")
    yield
    i18n.set_language("pt")


@pytest.fixture(autouse=True)
def _fresh_user_data():
    """Each test starts with no saved mission, profile or config (the folders live in a temp dir)."""
    import shutil

    from tenhut.services.platform import AppPaths

    paths = AppPaths.detect()
    for d in (paths.state_dir, paths.config_dir):
        shutil.rmtree(d, ignore_errors=True)
    yield


@pytest.fixture
def cfg():
    from tenhut.core import Settings

    return Settings()
