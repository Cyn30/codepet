import json
import struct
import unittest
from pathlib import Path

from codepet.domain import BREEDS

ASSETS = Path(__file__).resolve().parents[1] / "src" / "codepet" / "assets" / "animations"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Not a PNG file: {path}")
    return struct.unpack(">II", data[16:24])


class AnimationAssetTests(unittest.TestCase):
    def test_every_supported_breed_has_a_runtime_atlas(self):
        manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
        expected_size = (
            manifest["frame_width"] * manifest["columns"],
            manifest["frame_height"] * manifest["rows"],
        )
        for breed in BREEDS["cat"] + BREEDS["dog"]:
            slug = breed.lower().replace(" ", "-")
            atlas = ASSETS / f"{slug}.png"
            with self.subTest(breed=breed):
                self.assertTrue(atlas.exists())
                self.assertEqual(png_size(atlas), expected_size)


if __name__ == "__main__":
    unittest.main()
