import csv
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ft3_tools.catalog import load_catalog
from ft3_tools.export import OUTPUTS, _csv_bytes, _json_bytes, render_catalog, write_outputs


ROOT = Path(__file__).resolve().parents[1]


class ExportTests(unittest.TestCase):
    def test_fixed_wire_dialect(self):
        self.assertEqual(
            _csv_bytes(({"id": "FT001", "description": 'one,\n"two"'},), ("id", "description")),
            b'id,description\r\nFT001,"one,\n""two"""',
        )
        self.assertEqual(
            _json_bytes(({"id": "FT001", "description": "caf\u00e9\nnext"},)),
            b'[\n    {\n        "id": "FT001",\n        "description": "caf\\u00e9\\nnext"\n    }\n]',
        )

    def test_initial_artifacts_have_exact_adjudicated_cells(self):
        catalog = load_catalog(ROOT)
        rendered = render_catalog(catalog)
        self.assertEqual(set(rendered), set(OUTPUTS))
        self.assertEqual(rendered["FT3_Techniques.json"], (ROOT / "FT3_Techniques.json").read_bytes())
        self.assertEqual(
            rendered["Fraud Tools Tactics and Techniques - FT3 - Tactics.csv"],
            (ROOT / "Fraud Tools Tactics and Techniques - FT3 - Tactics.csv").read_bytes(),
        )
        technique_csv = list(csv.DictReader(io.StringIO(
            rendered["Fraud Tools Tactics and Techniques - FT3 - Techniques.csv"].decode("utf-8"), newline=""
        )))
        tactic_json = json.loads(rendered["FT3_Tactics.json"])
        self.assertEqual([row["id"] for row in technique_csv if row["name"] == "3DS Bypass"], ["FT056"])
        self.assertTrue(all(row["domain"] == "ft3" for row in tactic_json))
        self.assertEqual(rendered, render_catalog(catalog))

    def test_build_then_check_and_stale_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            build = subprocess.run(
                [sys.executable, "-m", "ft3_tools", "build", "--root", str(root)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            check = subprocess.run(
                [sys.executable, "-m", "ft3_tools", "check", "--root", str(root)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(check.returncode, 0, check.stderr)
            path = root / "FT3_Techniques.json"
            path.write_bytes(path.read_bytes() + b"\n")
            stale = subprocess.run(
                [sys.executable, "-m", "ft3_tools", "check", "--root", str(root)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(stale.returncode, 1)
            self.assertIn("FT3_Techniques.json", stale.stderr)

    def test_invalid_source_cannot_overwrite_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            existing = root / "FT3_Techniques.json"
            existing.write_bytes(b"previous output")
            source = root / "catalog/techniques/FT001.yaml"
            source.write_text(source.read_text(encoding="utf-8") + "id: duplicate\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "ft3_tools", "build", "--root", str(root)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(existing.read_bytes(), b"previous output")

    def test_build_preserves_readable_artifact_permissions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            for name in OUTPUTS:
                path = root / name
                path.write_bytes(b"prior")
                path.chmod(0o644)
            result = subprocess.run(
                [sys.executable, "-m", "ft3_tools", "build", "--root", str(root)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(all((root / name).stat().st_mode & 0o777 == 0o644 for name in OUTPUTS))

    def test_invalid_output_target_does_not_partially_replace(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            for name in OUTPUTS:
                path = root / name
                if name == OUTPUTS[2]:
                    path.mkdir()
                else:
                    path.write_bytes(b"prior")
            result = subprocess.run(
                [sys.executable, "-m", "ft3_tools", "build", "--root", str(root)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual((root / OUTPUTS[0]).read_bytes(), b"prior")
            self.assertEqual((root / OUTPUTS[1]).read_bytes(), b"prior")

    def test_check_rejects_external_output_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "public"
            root.mkdir()
            shutil.copytree(ROOT / "catalog", root / "catalog")
            rendered = render_catalog(load_catalog(root))
            for name in OUTPUTS:
                (root / name).write_bytes(rendered[name])
            outside = Path(temp) / "private-output"
            outside.write_bytes(rendered[OUTPUTS[0]])
            (root / OUTPUTS[0]).unlink()
            (root / OUTPUTS[0]).symlink_to(outside)
            result = subprocess.run(
                [sys.executable, "-m", "ft3_tools", "check", "--root", str(root)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)

    def test_replacement_failure_restores_previous_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            for name in OUTPUTS:
                (root / name).write_bytes(f"prior:{name}".encode("utf-8"))
            rendered = render_catalog(load_catalog(root))
            original_replace = __import__("os").replace
            calls = 0

            def fail_third_replace(source, destination):
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("injected replacement failure")
                return original_replace(source, destination)

            with patch("ft3_tools.export.os.replace", side_effect=fail_third_replace):
                with self.assertRaisesRegex(OSError, "injected replacement failure"):
                    write_outputs(root, rendered)
            for name in OUTPUTS:
                self.assertEqual((root / name).read_bytes(), f"prior:{name}".encode("utf-8"))
