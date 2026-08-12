"""Normalize approved chroma-key strips into a validated CodePet atlas."""

from __future__ import annotations

import argparse
import json
from itertools import pairwise
from pathlib import Path


def _dependencies():
    try:
        from PIL import Image, ImageChops, ImageDraw
    except ImportError as exc:
        raise SystemExit(
            "Install Pillow or use the bundled Codex workspace Python runtime"
        ) from exc
    return Image, ImageChops, ImageDraw


def occupied_bounds(image) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("Animation strip contains no visible pixels")
    return bounds


def split_strip(image, frame_count: int = 8, action: str = "idle"):
    """Split strips on transparent gutters or on their regular frame pitch."""
    alpha = image.getchannel("A")
    occupied = []
    for x in range(image.width):
        column = alpha.crop((x, 0, x + 1, image.height))
        occupied.append(column.getbbox() is not None)

    runs: list[tuple[int, int]] = []
    start: int | None = None
    for x, visible in enumerate(occupied + [False]):
        if visible and start is None:
            start = x
        elif not visible and start is not None:
            if x - start >= max(3, image.width // 100):
                runs.append((start, x))
            start = None
    if action not in {"walking", "running"} and len(runs) == frame_count:
        return [image.crop((left, 0, right, image.height)) for left, right in runs]

    detected = _split_by_foreground_components(
        image, frame_count, prefer_components=action in {"walking", "running"}
    )
    if detected is not None:
        return detected

    if len(runs) > frame_count:
        centers = [(left + right) / 2 for left, right in runs]
        differences = [right - left for left, right in pairwise(centers)]
        pitch = sorted(differences)[len(differences) // 2]
        for offset in range(frame_count):
            anchors = centers[offset : offset + frame_count]
            if len(anchors) < frame_count:
                break
            expected = [anchors[0] + pitch * index for index in range(frame_count)]
            if max(abs(actual - target) for actual, target in zip(anchors, expected)) < pitch * 0.35:
                boundaries = [
                    max(0, min(image.width, round(center - pitch / 2)))
                    for center in expected
                ]
                boundaries.append(max(0, min(image.width, round(expected[-1] + pitch / 2))))
                return [
                    image.crop((boundaries[index], 0, boundaries[index + 1], image.height))
                    for index in range(frame_count)
                ]

    width, height = image.size
    return [
        image.crop(
            (
                round(i * width / frame_count),
                0,
                round((i + 1) * width / frame_count),
                height,
            )
        )
        for i in range(frame_count)
    ]


def _split_by_foreground_components(
    image, frame_count: int, *, prefer_components: bool
):
    """Group alpha components by the repeated horizontal frame pitch."""
    try:
        import numpy as np
    except ImportError:
        return None

    alpha = np.asarray(image.getchannel("A")) >= 32
    height, width = alpha.shape
    visited = np.zeros_like(alpha, dtype=bool)
    components: list[tuple[int, int, int, int, int]] = []
    for y in range(height):
        for x in range(width):
            if not alpha[y, x] or visited[y, x]:
                continue
            stack = [(x, y)]
            visited[y, x] = True
            left = right = x
            top = bottom = y
            area = 0
            while stack:
                cx, cy = stack.pop()
                area += 1
                left, right = min(left, cx), max(right, cx)
                top, bottom = min(top, cy), max(bottom, cy)
                for nx, ny in (
                    (cx - 1, cy),
                    (cx + 1, cy),
                    (cx, cy - 1),
                    (cx, cy + 1),
                ):
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and alpha[ny, nx]
                        and not visited[ny, nx]
                    ):
                        visited[ny, nx] = True
                        stack.append((nx, ny))
            if area >= 10:
                components.append((left, top, right + 1, bottom + 1, area))

    major = sorted(components, key=lambda item: item[4], reverse=True)[:frame_count]
    if prefer_components and len(major) == frame_count:
        major.sort(key=lambda item: (item[0] + item[2]) / 2)
        return [
            image.crop((max(0, left - 2), 0, min(width, right + 2), height))
            for left, _, right, _, _ in major
        ]

    pitch = width / frame_count
    column_coverage = alpha.sum(axis=0)
    boundaries = [0]
    search_radius = pitch * 0.3
    for index in range(1, frame_count):
        expected = index * pitch
        left = max(boundaries[-1] + 1, round(expected - search_radius))
        right = min(width - 1, round(expected + search_radius))
        if left >= right:
            return None
        scores = []
        for x in range(left, right):
            score = int(column_coverage[max(0, x - 2) : min(width, x + 3)].sum())
            scores.append((score, abs(x - expected), x))
        boundaries.append(min(scores)[2])
    boundaries.append(width)
    if any(
        right - left < width / frame_count * 0.55
        for left, right in pairwise(boundaries)
    ):
        return None
    return [
        image.crop((boundaries[index] + 1, 0, boundaries[index + 1] - 1, height))
        for index in range(frame_count)
    ]


def normalize_frame(frame, frame_size: int, padding: int, scale: float, Image):
    bounds = occupied_bounds(frame)
    visible = frame.crop(bounds)
    visible = _remove_small_components(visible, Image)
    bounds = occupied_bounds(visible)
    visible = visible.crop(bounds)
    target_size = (
        max(1, round(visible.width * scale)),
        max(1, round(visible.height * scale)),
    )
    resized = visible.resize(target_size, Image.Resampling.NEAREST)
    cell = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
    x = (frame_size - resized.width) // 2
    y = frame_size - padding - resized.height
    cell.alpha_composite(resized, (x, y))
    return cell


def _remove_small_components(image, Image):
    """Remove detached chroma-key debris while preserving meaningful effects."""
    try:
        import numpy as np
    except ImportError:
        return image
    alpha = np.asarray(image.getchannel("A")) >= 32
    height, width = alpha.shape
    visited = np.zeros_like(alpha, dtype=bool)
    components: list[list[tuple[int, int]]] = []
    for y in range(height):
        for x in range(width):
            if not alpha[y, x] or visited[y, x]:
                continue
            stack = [(x, y)]
            visited[y, x] = True
            pixels = []
            while stack:
                cx, cy = stack.pop()
                pixels.append((cx, cy))
                for nx, ny in (
                    (cx - 1, cy),
                    (cx + 1, cy),
                    (cx, cy - 1),
                    (cx, cy + 1),
                ):
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and alpha[ny, nx]
                        and not visited[ny, nx]
                    ):
                        visited[ny, nx] = True
                        stack.append((nx, ny))
            components.append(pixels)
    if not components:
        return image
    largest = max(len(component) for component in components)
    keep = np.zeros_like(alpha, dtype=np.uint8)
    for component in components:
        if len(component) >= max(24, largest * 0.12):
            for x, y in component:
                keep[y, x] = 255
    cleaned = image.copy()
    original_alpha = image.getchannel("A")
    cleaned.putalpha(Image.fromarray(np.minimum(np.asarray(original_alpha), keep), mode="L"))
    return cleaned


def build_atlas(source: Path, destination: Path, manifest_path: Path) -> None:
    Image, _, _ = _dependencies()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    frame_size = manifest["frame_width"]
    if frame_size != manifest["frame_height"]:
        raise ValueError("Only square animation frames are supported")
    atlas = Image.new(
        "RGBA",
        (frame_size * manifest["columns"], frame_size * manifest["rows"]),
        (0, 0, 0, 0),
    )
    for action, row in manifest["actions"].items():
        strip_path = source / f"{action}.png"
        strip = Image.open(strip_path).convert("RGBA")
        frames = split_strip(strip, manifest["columns"], action)
        visible_sizes = []
        for frame in frames:
            left, top, right, bottom = occupied_bounds(frame)
            visible_sizes.append((right - left, bottom - top))
        available = frame_size - 10
        scale = min(
            available / max(width for width, _ in visible_sizes),
            available / max(height for _, height in visible_sizes),
        )
        for column, frame in enumerate(frames):
            normalized = normalize_frame(
                frame, frame_size, padding=5, scale=scale, Image=Image
            )
            atlas.alpha_composite(normalized, (column * frame_size, row * frame_size))
    destination.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(destination, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("assets/animations/manifest.json"),
    )
    args = parser.parse_args()
    build_atlas(args.source, args.out, args.manifest)


if __name__ == "__main__":
    main()
