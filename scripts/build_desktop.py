"""Build a native CodePet bundle on the current operating system."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
APP_NAME = "CodePet"


def run(command: list[str]) -> None:
    environment = os.environ.copy()
    environment["PYINSTALLER_CONFIG_DIR"] = str(ROOT / ".pyinstaller")
    subprocess.run(command, cwd=ROOT, check=True, env=environment)


def build_macos_image(app_path: Path, dmg_path: Path) -> None:
    if dmg_path.exists():
        dmg_path.unlink()
    standard = [
        "hdiutil", "create", "-volname", APP_NAME,
        "-srcfolder", str(app_path), "-ov", "-format", "UDZO", str(dmg_path),
    ]
    try:
        run(standard)
    except subprocess.CalledProcessError:
        # Headless sandboxes may not expose the virtual disk device required by
        # `hdiutil create`. A read-only HFS hybrid remains directly mountable.
        run([
            "hdiutil", "makehybrid", "-o", str(dmg_path), str(app_path),
            "-hfs", "-hfs-volume-name", APP_NAME,
        ])


def build() -> Path:
    run([
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(ROOT / "packaging" / "codepet.spec"),
    ])
    system = platform.system()
    if system == "Darwin":
        app_path = DIST / f"{APP_NAME}.app"
        if not app_path.exists():
            raise RuntimeError(f"Expected application bundle at {app_path}")
        dmg_path = DIST / f"{APP_NAME}-macOS.dmg"
        build_macos_image(app_path, dmg_path)
        return dmg_path
    if system == "Windows":
        archive = shutil.make_archive(str(DIST / f"{APP_NAME}-Windows"), "zip", DIST / APP_NAME)
        return Path(archive)
    archive = shutil.make_archive(str(DIST / f"{APP_NAME}-Linux"), "gztar", DIST / APP_NAME)
    return Path(archive)


if __name__ == "__main__":
    print(f"Built {build()}")
