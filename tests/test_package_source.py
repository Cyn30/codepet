import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.package_source import ROOT, build_archive


class SourcePackageTests(unittest.TestCase):
    def test_archive_contains_source_without_generated_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "source.zip"
            build_archive(destination)
            with zipfile.ZipFile(destination) as archive:
                names = set(archive.namelist())

        self.assertIn("README.md", names)
        self.assertIn("src/codepet/desktop.py", names)
        self.assertIn("website/package-lock.json", names)
        self.assertIn("website/build/sites-vite-plugin.ts", names)
        self.assertNotIn("outputs/CodePet-v0.4.0-source.zip", names)
        for name in names:
            parts = Path(name).parts
            self.assertNotIn("node_modules", parts)
            self.assertNotIn("__pycache__", parts)
            self.assertNotIn(".pytest_cache", parts)
            self.assertNotIn("dist", parts)

    def test_every_packaged_file_is_below_githubs_hard_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "source.zip"
            build_archive(destination)
            with zipfile.ZipFile(destination) as archive:
                largest = max(info.file_size for info in archive.infolist())
        self.assertLess(largest, 100 * 1024 * 1024)
        self.assertTrue(ROOT.is_dir())


if __name__ == "__main__":
    unittest.main()
