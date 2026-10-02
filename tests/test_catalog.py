import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from ft3_tools.catalog import CatalogError, TACTIC_FIELDS, TECHNIQUE_FIELDS, load_catalog


ROOT = Path(__file__).resolve().parents[1]


def write_fixture(root: Path, *, tactic=None, technique=None, order=None, exceptions=None):
    tactic = tactic or {
        "ID": "FTA001", "stix_id": "", "name": "Reconnaissance",
        "description": "A tactic", "url": "", "created": "01/30/2024",
        "last_modified": "01/30/2024", "domain": "ft3", "version": "V.1",
    }
    technique = technique or {
        "id": "FT001", "stix_id": "", "name": "Example", "description": "A technique",
        "url": "", "created": "1/30/24", "last_modified": "1/30/24",
        "domain": "ft3", "version": "V.1", "tactics": "Reconnaissance",
        "detection": "", "data sources": "", "is_sub-technique": "FALSE",
        "sub-technique of": "", "defenses_bypassed": "", "contributors": "",
        "permissions_required": "", "supports_remote": "", "system_requirements": "",
        "impact_type": "", "effective_permissions": "", "relationship_citations": "",
    }
    (root / "catalog/tactics").mkdir(parents=True, exist_ok=True)
    (root / "catalog/techniques").mkdir(parents=True, exist_ok=True)
    (root / f"catalog/tactics/{tactic['ID']}.yaml").write_text(
        yaml.safe_dump(tactic, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    (root / f"catalog/techniques/{technique['id']}.yaml").write_text(
        yaml.safe_dump(technique, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    (root / "catalog/order.yaml").write_text(
        yaml.safe_dump(order or {"tactics": [tactic["ID"]], "techniques": [technique["id"]]}, sort_keys=False),
        encoding="utf-8",
    )
    (root / "catalog/reference-exceptions.json").write_text(
        json.dumps({"schema_version": 1, "findings": exceptions or []}), encoding="utf-8"
    )


class CatalogTests(unittest.TestCase):
    def test_loads_exact_legacy_string_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            catalog = load_catalog(root)
            self.assertEqual(tuple(catalog.tactics[0]), TACTIC_FIELDS)
            self.assertEqual(tuple(catalog.techniques[0]), TECHNIQUE_FIELDS)
            self.assertEqual(catalog.techniques[0]["is_sub-technique"], "FALSE")

    def test_rejects_implicit_boolean_and_duplicate_key(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            path = root / "catalog/techniques/FT001.yaml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("'FALSE'", "FALSE"), encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "must be a string"):
                load_catalog(root)
            path.write_text(text + "id: FT002\n", encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "duplicate key"):
                load_catalog(root)

    def test_rejects_yaml_anchors_and_unknown_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            path = root / "catalog/techniques/FT001.yaml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("id: FT001", "id: &shared FT001"), encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "anchors and aliases"):
                load_catalog(root)
            path.write_text(text + "unexpected: value\n", encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "unknown fields"):
                load_catalog(root)

    def test_rejects_explicit_tags_merge_keys_and_multiple_documents(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            path = root / "catalog/techniques/FT001.yaml"
            text = path.read_text(encoding="utf-8")
            for payload, expected in (
                (text.replace("id: FT001", "id: !!str FT001"), "tags"),
                (text + "<<: {}\n", "merge keys"),
                (text + "---\nvalue\n", "cannot read YAML"),
            ):
                with self.subTest(expected=expected):
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(CatalogError, expected):
                        load_catalog(root)

    def test_manifest_and_reference_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            (root / "catalog/order.yaml").write_text("tactics: [FTA001]\ntechniques: []\n", encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "order manifest"):
                load_catalog(root)
            write_fixture(root)
            path = root / "catalog/techniques/FT001.yaml"
            text = path.read_text(encoding="utf-8").replace("tactics: Reconnaissance", "tactics: Missing")
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "reference findings"):
                load_catalog(root)

    def test_rejects_catalog_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "public"
            write_fixture(root)
            source = root / "catalog/techniques/FT001.yaml"
            outside = Path(temp) / "private.yaml"
            outside.write_bytes(source.read_bytes())
            source.unlink()
            source.symlink_to(outside)
            with self.assertRaisesRegex(CatalogError, "symlink"):
                load_catalog(root)

    def test_exact_reference_exception_is_visible_and_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            technique = {
                "id": "FT001", "stix_id": "", "name": "Example", "description": "A technique",
                "url": "", "created": "1/30/24", "last_modified": "1/30/24",
                "domain": "ft3", "version": "V.1", "tactics": "Missing",
                "detection": "", "data sources": "", "is_sub-technique": "FALSE",
                "sub-technique of": "", "defenses_bypassed": "", "contributors": "",
                "permissions_required": "", "supports_remote": "", "system_requirements": "",
                "impact_type": "", "effective_permissions": "", "relationship_citations": "",
            }
            exception = {"rule": "unknown-tactic", "id": "FT001", "field": "tactics", "value": "Missing"}
            write_fixture(root, technique=technique, exceptions=[exception])
            catalog = load_catalog(root)
            self.assertEqual(catalog.reference_findings, (exception,))

    def test_new_wrong_existing_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            path = root / "catalog/techniques/FT005.001.yaml"
            text = path.read_text(encoding="utf-8")
            self.assertIn("sub-technique of: FT005", text)
            path.write_text(text.replace("sub-technique of: FT005", "sub-technique of: FT007"), encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "parent-prefix-mismatch"):
                load_catalog(root)

    def test_domain_is_v1_catalog_domain(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_fixture(root)
            path = root / "catalog/tactics/FTA001.yaml"
            path.write_text(path.read_text(encoding="utf-8").replace("domain: ft3", "domain: fraud-attack"), encoding="utf-8")
            with self.assertRaisesRegex(CatalogError, "domain"):
                load_catalog(root)
