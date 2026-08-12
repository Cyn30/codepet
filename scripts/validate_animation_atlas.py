"""Fail when an animation atlas has missing or nearly empty frames."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(atlas_path: Path, manifest_path: Path) -> list[str]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Install Pillow to validate animation artwork") from exc
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    atlas = Image.open(atlas_path).convert("RGBA")
    frame_width = manifest["frame_width"]
    frame_height = manifest["frame_height"]
    expected = (frame_width * manifest["columns"], frame_height * manifest["rows"])
    errors: list[str] = []
    if atlas.size != expected:
        return [f"expected {expected[0]}x{expected[1]}, got {atlas.width}x{atlas.height}"]
    for action, row in manifest["actions"].items():
        for column in range(manifest["columns"]):
            frame = atlas.crop(
                (
                    column * frame_width,
                    row * frame_height,
                    (column + 1) * frame_width,
                    (row + 1) * frame_height,
                )
            )
            alpha = frame.getchannel("A")
            pixels = (
                alpha.get_flattened_data()
                if hasattr(alpha, "get_flattened_data")
                else alpha.getdata()
            )
            visible_pixels = sum(1 for value in pixels if value >= 32)
            if visible_pixels < frame_width * frame_height * 0.025:
                errors.append(f"{action} frame {column + 1} is empty or too small")
            if alpha.getbbox() is None:
                errors.append(f"{action} frame {column + 1} has no alpha coverage")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("atlas", type=Path)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("assets/animations/manifest.json"),
    )
    args = parser.parse_args()
    errors = validate(args.atlas, args.manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {args.atlas}")


if __name__ == "__main__":
    main()
