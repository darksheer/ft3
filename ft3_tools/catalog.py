"""Load and validate the authored FT3 V1 YAML catalog."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from yaml.events import AliasEvent


TACTIC_FIELDS = (
    "ID", "stix_id", "name", "description", "url", "created", "last_modified",
    "domain", "version",
)
TECHNIQUE_FIELDS = (
    "id", "stix_id", "name", "description", "url", "created", "last_modified",
    "domain", "version", "tactics", "detection", "data sources", "is_sub-technique",
    "sub-technique of", "defenses_bypassed", "contributors", "permissions_required",
    "supports_remote", "system_requirements", "impact_type", "effective_permissions",
    "relationship_citations",
)
TACTIC_ID = re.compile(r"FTA[0-9]{3}\Z")
TECHNIQUE_ID = re.compile(r"FT[0-9]{3}(?:\.[0-9]{3})?\Z")
REFERENCE_KEYS = ("rule", "id", "field", "value")


class CatalogError(ValueError):
    """Invalid authored catalog or policy."""


class StrictLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        event = self.peek_event()
        if isinstance(event, AliasEvent) or getattr(event, "anchor", None):
            raise CatalogError("YAML anchors and aliases are not allowed")
        if getattr(event, "tag", None) is not None:
            raise CatalogError("explicit YAML tags are not allowed")
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise CatalogError("YAML merge keys are not allowed")
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise CatalogError("YAML mapping keys must be strings")
            if key in result:
                raise CatalogError(f"duplicate key: {key}")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


@dataclass(frozen=True)
class Catalog:
    tactics: tuple[dict[str, str], ...]
    techniques: tuple[dict[str, str], ...]
    reference_findings: tuple[dict[str, str], ...]


def _load_yaml(path: Path):
    if path.is_symlink():
        raise CatalogError(f"{path}: catalog symlink is not allowed")
    try:
        with path.open(encoding="utf-8") as source:
            return yaml.load(source, Loader=StrictLoader)
    except CatalogError as exc:
        raise CatalogError(f"{path}: {exc}") from exc
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise CatalogError(f"{path}: cannot read YAML: {exc}") from exc


def _order(root: Path) -> dict[str, list[str]]:
    order = _load_yaml(root / "catalog/order.yaml")
    if not isinstance(order, dict) or set(order) != {"tactics", "techniques"}:
        raise CatalogError("order manifest must contain tactics and techniques lists")
    for kind, pattern in (("tactics", TACTIC_ID), ("techniques", TECHNIQUE_ID)):
        ids = order[kind]
        if (not isinstance(ids, list) or not all(isinstance(v, str) and pattern.fullmatch(v) for v in ids)
                or len(ids) != len(set(ids))):
            raise CatalogError(f"order manifest has invalid or duplicate {kind} IDs")
    return order


def _records(root: Path, kind: str, ids: list[str], fields: tuple[str, ...], pattern: re.Pattern) -> tuple[dict[str, str], ...]:
    directory = root / "catalog" / kind
    if directory.is_symlink():
        raise CatalogError(f"{directory}: catalog symlink is not allowed")
    paths = sorted(directory.glob("*.yaml"))
    actual = {path.stem for path in paths}
    if len(paths) != len(actual) or actual != set(ids):
        raise CatalogError(f"order manifest does not match {kind} files")
    key = "ID" if kind == "tactics" else "id"
    result = []
    for record_id in ids:
        path = directory / f"{record_id}.yaml"
        record = _load_yaml(path)
        if not isinstance(record, dict):
            raise CatalogError(f"{path}: record must be a mapping")
        missing = set(fields) - set(record)
        unknown = set(record) - set(fields)
        if unknown:
            raise CatalogError(f"{path}: unknown fields: {', '.join(sorted(unknown))}")
        if missing:
            raise CatalogError(f"{path}: missing fields: {', '.join(sorted(missing))}")
        for field in fields:
            if not isinstance(record[field], str):
                raise CatalogError(f"{path}: {field} must be a string")
        if record[key] != record_id or not pattern.fullmatch(record[key]):
            raise CatalogError(f"{path}: {key} must match filename and ID grammar")
        result.append({field: record[field] for field in fields})
    return tuple(result)


def _reference_findings(tactics: tuple[dict[str, str], ...], techniques: tuple[dict[str, str], ...]) -> tuple[dict[str, str], ...]:
    tactic_names = [row["name"] for row in tactics]
    if len(tactic_names) != len(set(tactic_names)) or any(not name for name in tactic_names):
        raise CatalogError("tactic names must be unique and nonempty")
    if any(row["domain"] != "ft3" for row in tactics + techniques):
        raise CatalogError("domain must be ft3 for every V1 record")
    technique_ids = {row["id"] for row in techniques}
    findings = []
    for row in techniques:
        record_id = row["id"]
        is_child = "." in record_id
        expected_flag = "TRUE" if is_child else "FALSE"
        if row["is_sub-technique"] != expected_flag:
            raise CatalogError(f"{record_id}: is_sub-technique must be {expected_flag}")
        if row["tactics"] not in tactic_names:
            findings.append({"rule": "unknown-tactic", "id": record_id,
                             "field": "tactics", "value": row["tactics"]})
        parent = row["sub-technique of"]
        if parent and parent not in technique_ids:
            findings.append({"rule": "unknown-parent", "id": record_id,
                             "field": "sub-technique of", "value": parent})
        if is_child and parent in technique_ids and parent != record_id.split(".")[0]:
            findings.append({"rule": "parent-prefix-mismatch", "id": record_id,
                             "field": "sub-technique of", "value": parent})
        if is_child and not parent:
            findings.append({"rule": "missing-parent", "id": record_id,
                             "field": "sub-technique of", "value": ""})
        if not is_child and parent:
            findings.append({"rule": "unexpected-parent", "id": record_id,
                             "field": "sub-technique of", "value": parent})
    return tuple(sorted(findings, key=lambda finding: tuple(finding[key] for key in REFERENCE_KEYS)))


def _expected_findings(root: Path) -> tuple[dict[str, str], ...]:
    path = root / "catalog/reference-exceptions.json"
    if path.is_symlink():
        raise CatalogError(f"{path}: catalog symlink is not allowed")
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"{path}: cannot read reference exceptions: {exc}") from exc
    if not isinstance(policy, dict) or set(policy) != {"schema_version", "findings"} or policy["schema_version"] != 1:
        raise CatalogError(f"{path}: invalid reference exception policy")
    findings = policy["findings"]
    if not isinstance(findings, list) or any(
        not isinstance(item, dict) or set(item) != set(REFERENCE_KEYS)
        or not all(isinstance(item[key], str) for key in REFERENCE_KEYS)
        for item in findings
    ):
        raise CatalogError(f"{path}: invalid reference findings")
    tuples = [tuple(item[key] for key in REFERENCE_KEYS) for item in findings]
    if len(tuples) != len(set(tuples)):
        raise CatalogError(f"{path}: duplicate reference findings")
    return tuple(sorted(findings, key=lambda finding: tuple(finding[key] for key in REFERENCE_KEYS)))


def load_catalog(root: Path) -> Catalog:
    """Return ordered V1 records after strict structural and reference checks."""
    if (root / "catalog").is_symlink():
        raise CatalogError("catalog symlink is not allowed")
    order = _order(root)
    tactics = _records(root, "tactics", order["tactics"], TACTIC_FIELDS, TACTIC_ID)
    techniques = _records(root, "techniques", order["techniques"], TECHNIQUE_FIELDS, TECHNIQUE_ID)
    findings = _reference_findings(tactics, techniques)
    expected = _expected_findings(root)
    if findings != expected:
        added = [finding for finding in findings if finding not in expected]
        removed = [finding for finding in expected if finding not in findings]
        raise CatalogError(f"reference findings differ from accepted policy: new={added}, stale={removed}")
    return Catalog(tactics=tactics, techniques=techniques, reference_findings=findings)
