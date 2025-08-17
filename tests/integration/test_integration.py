import difflib
import filecmp
import os
import shutil
from pathlib import Path
from unittest import TestCase


class IntegrationBase(TestCase):
    set_name: str

    def setUp(self):
        self.expected_path = Path(
            f"tests/integration/{self.set_name}/expected"
        )
        self.source_dir = Path(f"tests/integration/{self.set_name}/unmodified")
        self.test_dir = Path(
            f"tests/integration/{self.set_name}/unmodified_test"
        )
        self.root = os.getcwd()

        if not self.source_dir.exists():
            raise FileNotFoundError(
                f"Source directory '{self.source_dir}' does not exist."
            )
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

        shutil.copytree(self.source_dir, self.test_dir)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def compare_directories(self, dir1: Path | str, dir2: Path | str):
        """Compares two directories recursively and shows exact file differences."""
        comparison = filecmp.dircmp(dir1, dir2)

        # Files/folders only in one directory
        self.assertListEqual(
            sorted(comparison.left_only),
            [],
            f"Items only in {dir1}: {comparison.left_only}",
        )
        self.assertListEqual(
            sorted(comparison.right_only),
            [],
            f"Items only in {dir2}: {comparison.right_only}",
        )
        self.assertListEqual(
            sorted(comparison.funny_files),
            [],
            f"Problematic files in comparison: {comparison.funny_files}",
        )

        # Detailed diff of differing files
        for filename in comparison.diff_files:
            path1 = os.path.join(dir1, filename)
            path2 = os.path.join(dir2, filename)

            with open(path1, "r", encoding="utf-8") as f1, open(
                path2, "r", encoding="utf-8"
            ) as f2:
                lines1 = f1.readlines()
                lines2 = f2.readlines()

            diff = difflib.unified_diff(
                lines1,
                lines2,
                fromfile=str(path1),
                tofile=str(path2),
                lineterm="",
            )

            diff_text = "\n".join(diff)
            self.fail(
                f"Files differ between {path1} and {path2}:\n{diff_text}"
            )

        # Recurse into common subdirectories
        for subdir in comparison.common_dirs:
            self.compare_directories(
                os.path.join(dir1, subdir), os.path.join(dir2, subdir)
            )
