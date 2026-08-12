"""Create a clean source archive without local dependencies or build output."""

from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {
    ".git",
    ".idea",
    ".next",
    ".pyinstaller",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vinext",
    ".vscode",
    ".wrangler",
    "__pycache__",
    "dist",
    "node_modules",
}
EXCLUDED_ROOT_DIRECTORIES = {"build", "dist", "outputs", "work"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
MAX_REPOSITORY_FILE_BYTES = 100 * 1024 * 1024


def included_files() -> list[Path]:
    files: list[Path] = []
    for directory, names, filenames in os.walk(ROOT):
        current = Path(directory)
        relative_directory = current.relative_to(ROOT)
        names[:] = sorted(
            name
            for name in names
            if name not in EXCLUDED_PARTS
            and not name.endswith(".egg-info")
            and not (current == ROOT and name in EXCLUDED_ROOT_DIRECTORIES)
        )
        for filename in sorted(filenames):
            path = current / filename
            relative = relative_directory / filename
            if filename == ".DS_Store" or path.suffix in EXCLUDED_SUFFIXES:
                continue
            if path.stat().st_size >= MAX_REPOSITORY_FILE_BYTES:
                raise ValueError(f"Repository file is at least 100 MiB: {relative}")
            files.append(path)
    return files


def build_archive(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in included_files():
            archive.write(path, PurePosixPath(path.relative_to(ROOT)).as_posix())
    temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        default=ROOT / "outputs" / "CodePet-source.zip",
    )
    args = parser.parse_args()
    build_archive(args.destination.resolve())
    print(f"Built {args.destination.resolve()}")


if __name__ == "__main__":
    main()
