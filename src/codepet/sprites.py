"""Validated animation atlases with a legacy still-frame fallback."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap

from .animation import CLIPS
from .domain import BREEDS, Pet

ACTION_ROWS = {"idle": 0, "walking": 1, "sleeping": 2, "eating": 3}
BREED_COLUMNS = {
    breed: index
    for index, breed in enumerate(BREEDS["cat"] + BREEDS["dog"])
}


class SpriteSheet:
    def __init__(self) -> None:
        self.assets_path = Path(__file__).resolve().parent / "assets"
        path = self.assets_path / "pet-actions.png"
        self._pixmap = QPixmap(str(path))
        if self._pixmap.isNull():
            raise RuntimeError(f"Unable to load pet sprites from {path}")
        self._atlases: dict[str, QPixmap | None] = {}
        self._manifest = self._load_manifest()

    def frame(self, pet: Pet, action: str = "idle", frame_index: int = 0) -> QPixmap:
        atlas = self._atlas(pet.breed)
        if atlas is not None:
            row = self._manifest["actions"][action]
            frame_width = self._manifest["frame_width"]
            frame_height = self._manifest["frame_height"]
            return atlas.copy(
                QRect(
                    (frame_index % CLIPS[action].frame_count) * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height,
                )
            )
        return self._legacy_frame(pet)

    def has_animation(self, breed: str) -> bool:
        return self._atlas(breed) is not None

    def _legacy_frame(self, pet: Pet) -> QPixmap:
        action = {
            "walking": "walking",
            "running": "walking",
            "resting": "sleeping",
            "eating": "eating",
        }.get(pet.mode, "idle")
        cell_width = self._pixmap.width() // 6
        cell_height = self._pixmap.height() // 4
        column = BREED_COLUMNS[pet.breed]
        row = ACTION_ROWS[action]
        return self._pixmap.copy(
            QRect(column * cell_width, row * cell_height, cell_width, cell_height)
        )

    def _atlas(self, breed: str) -> QPixmap | None:
        slug = re.sub(r"[^a-z0-9]+", "-", breed.lower()).strip("-")
        if slug not in self._atlases:
            path = self.assets_path / "animations" / f"{slug}.png"
            atlas = QPixmap(str(path))
            if atlas.isNull():
                self._atlases[slug] = None
            else:
                expected_width = self._manifest["frame_width"] * self._manifest["columns"]
                expected_height = self._manifest["frame_height"] * self._manifest["rows"]
                if (atlas.width(), atlas.height()) != (expected_width, expected_height):
                    raise RuntimeError(
                        f"Invalid animation atlas {path}: expected "
                        f"{expected_width}x{expected_height}, got {atlas.width()}x{atlas.height()}"
                    )
                self._atlases[slug] = atlas
        return self._atlases[slug]

    def _load_manifest(self) -> dict:
        path = self.assets_path / "animations" / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        expected_actions = set(CLIPS)
        if set(manifest.get("actions", {})) != expected_actions:
            raise RuntimeError(f"Animation manifest actions do not match runtime clips: {path}")
        if manifest.get("columns") != 8 or manifest.get("rows") != 6:
            raise RuntimeError(f"Animation manifest must use an 8 by 6 grid: {path}")
        return manifest
