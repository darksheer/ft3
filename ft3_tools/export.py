"""Deterministic V1 JSON and CSV projections from authored YAML."""

from __future__ import annotations

import csv
import io
import json
import os
import stat
import tempfile
from pathlib import Path

from .catalog import Catalog, TACTIC_FIELDS, TECHNIQUE_FIELDS


TACTIC_JSON = "FT3_Tactics.json"
TECHNIQUE_JSON = "FT3_Techniques.json"
TACTIC_CSV = "Fraud Tools Tactics and Techniques - FT3 - Tactics.csv"
TECHNIQUE_CSV = "Fraud Tools Tactics and Techniques - FT3 - Techniques.csv"
OUTPUTS = (TACTIC_JSON, TECHNIQUE_JSON, TACTIC_CSV, TECHNIQUE_CSV)


def _json_bytes(rows: tuple[dict[str, str], ...]) -> bytes:
    return json.dumps(rows, indent=4, ensure_ascii=True).encode("utf-8")


def _csv_bytes(rows: tuple[dict[str, str], ...], fields: tuple[str, ...]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(fields)
    for row in rows:
        writer.writerow([row[field] for field in fields])
    value = stream.getvalue()
    return value[:-2].encode("utf-8") if value.endswith("\r\n") else value.encode("utf-8")


def render_catalog(catalog: Catalog) -> dict[str, bytes]:
    """Render the four legacy artifact paths without reading or writing them."""
    return {
        TACTIC_JSON: _json_bytes(catalog.tactics),
        TECHNIQUE_JSON: _json_bytes(catalog.techniques),
        TACTIC_CSV: _csv_bytes(catalog.tactics, TACTIC_FIELDS),
        TECHNIQUE_CSV: _csv_bytes(catalog.techniques, TECHNIQUE_FIELDS),
    }


def stale_outputs(root: Path, rendered: dict[str, bytes]) -> list[str]:
    """Return missing or byte-stale artifact names in stable order."""
    stale = []
    for name in OUTPUTS:
        if (root / name).is_symlink():
            stale.append(name)
            continue
        try:
            actual = (root / name).read_bytes()
        except FileNotFoundError:
            stale.append(name)
        else:
            if actual != rendered[name]:
                stale.append(name)
    return stale


def write_outputs(root: Path, rendered: dict[str, bytes]) -> None:
    """Stage complete files, preserving modes and restoring outputs on failure."""
    staged = {}
    backups = {}
    replaced = []
    try:
        # Reject known invalid destinations before touching any output.
        for name in OUTPUTS:
            target = root / name
            if target.is_symlink() or (target.exists() and not target.is_file()):
                raise OSError(f"invalid generated output target: {target}")
        for name in OUTPUTS:
            target = root / name
            mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
            with tempfile.NamedTemporaryFile(prefix=".ft3-build-", dir=root, delete=False) as tmp:
                tmp.write(rendered[name])
                tmp.flush()
                os.fchmod(tmp.fileno(), mode)
                os.fsync(tmp.fileno())
                staged[name] = Path(tmp.name)
            if target.exists():
                with tempfile.NamedTemporaryFile(prefix=".ft3-backup-", dir=root, delete=False) as backup:
                    backup.write(target.read_bytes())
                    backup.flush()
                    os.fchmod(backup.fileno(), mode)
                    os.fsync(backup.fileno())
                    backups[name] = Path(backup.name)
            else:
                backups[name] = None
        for name in OUTPUTS:
            os.replace(staged[name], root / name)
            replaced.append(name)
    except OSError as failure:
        rollback_errors = []
        for name in reversed(replaced):
            try:
                backup = backups[name]
                if backup is None:
                    (root / name).unlink()
                else:
                    os.replace(backup, root / name)
            except OSError as error:
                rollback_errors.append(f"{name}: {error}")
        if rollback_errors:
            raise OSError(f"{failure}; rollback incomplete: {'; '.join(rollback_errors)}") from failure
        raise
    finally:
        for path in list(staged.values()) + [path for path in backups.values() if path is not None]:
            path.unlink(missing_ok=True)
