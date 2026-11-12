# PyInstaller spec for Tenhut. Run from the repository root:
#
#     uv sync --group build                                   # core build
#     uv sync --group build --extra camera                    # build with camera surveillance
#     TENHUT_FLAVOR=camera uv run pyinstaller packaging/tenhut.spec --noconfirm
#
# Output: dist/tenhut/ (Linux, Windows) or dist/Tenhut.app (macOS).
# The "core" flavor leaves out mediapipe/OpenCV: it is ~10x smaller and needs no camera permission use.
import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH).parent
FLAVOR = os.environ.get("TENHUT_FLAVOR", "core")
ICONS = ROOT / "packaging" / "icons"
VERSION = os.environ.get("TENHUT_VERSION", "0.0.0")

datas = [
    (str(ROOT / "src" / "tenhut" / "assets"), "tenhut/assets"),
    (str(ROOT / "helper" / "hosts-helper"), "helper"),  # Windows writes the hosts file with this, in-process
]
binaries, hiddenimports = [], []
excludes = ["tkinter", "unittest", "pydoc"]

if FLAVOR == "camera":
    for pkg in ("mediapipe", "cv2"):
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
else:
    excludes += ["mediapipe", "cv2", "numpy", "matplotlib"]

a = Analysis(
    [str(ROOT / "packaging" / "entry.py")],
    pathex=[str(ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=excludes,
    noarchive=False,
)
pyz = PYZ(a.pure)

icon = {"win32": ICONS / "icon.ico", "darwin": ICONS / "icon.icns"}.get(sys.platform)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="tenhut",
    console=False,
    icon=str(icon) if icon else None,
    # Windows: editing the hosts file needs administrator rights, so ask for them at launch (UAC prompt).
    uac_admin=(sys.platform == "win32"),
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="tenhut", upx=False)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Tenhut.app",
        icon=str(ICONS / "icon.icns"),
        bundle_identifier="io.github.eljonathas.tenhut",
        version=VERSION,
        info_plist={
            "CFBundleName": "Tenhut",
            "CFBundleDisplayName": "Tenhut",
            "CFBundleShortVersionString": VERSION,
            "NSHighResolutionCapable": True,
            "LSApplicationCategoryType": "public.app-category.productivity",
            "NSCameraUsageDescription": "Tenhut uses the camera, only if you turn it on, to notice when you look away from the screen during a work block.",
        },
    )
