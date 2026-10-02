import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ft3_tools.export import OUTPUTS


ROOT = Path(__file__).resolve().parents[1]


class PortabilityTests(unittest.TestCase):
    def test_public_only_copy_checks_without_sibling_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "ft3-public"
            root.mkdir()
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copytree(ROOT / "ft3_tools", root / "ft3_tools", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy2(ROOT / "requirements.txt", root / "requirements.txt")
            for name in OUTPUTS:
                shutil.copy2(ROOT / name, root / name)
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment["HOME"] = str(root)
            result = subprocess.run(
                [sys.executable, "-m", "ft3_tools", "check"], cwd=root,
                env=environment, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
