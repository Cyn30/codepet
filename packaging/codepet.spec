# PyInstaller specification for reproducible desktop bundles.

from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_submodules

project_root = Path(SPEC).resolve().parents[1]
source_root = project_root / "src"

analysis = Analysis(
    [str(project_root / "packaging" / "entrypoint.py")],
    pathex=[str(source_root)],
    binaries=[],
    datas=[(str(source_root / "codepet" / "assets"), "codepet/assets")],
    hiddenimports=collect_submodules("PySide6.QtSvg") + collect_submodules("keyring.backends"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest", "unittest"],
    noarchive=False,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="CodePet",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

collection = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CodePet",
)

if sys.platform == "darwin":
    app = BUNDLE(
        collection,
        name="CodePet.app",
        bundle_identifier="dev.codepet.desktop",
        info_plist={
            "CFBundleName": "CodePet",
            "CFBundleDisplayName": "CodePet",
            "CFBundleShortVersionString": "0.4.0",
            "NSHighResolutionCapable": True,
            "LSUIElement": False,
        },
    )
