# FT3 V1 YAML Source Implementation Plan

Status: implemented locally and verified; publication remains a separate maintainer action.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Make per-record YAML the public FT3 V1 source and deterministically generate the four existing JSON/CSV catalogs with the adjudicated values.

**Architecture:** A strict V1 YAML loader checks the source, order manifest, and known legacy reference defects. A pure projection serializes all four existing output paths. A small CLI provides read-only `check` and explicit `build`; tests and contributor docs close the public-only workflow.

**Tech Stack:** Python 3.12+, PyYAML 6.0.3, standard-library unittest, Git.

**Spec:** `docs/superpowers/specs/2026-10-01-ft3-v1-yaml-source-design.md`

## Global constraints

- Public V1 only; no imports, runtime reads, fixtures, schemas, or release gates from FT3 2.0.
- Preserve the 22 technique and nine tactic wire fields as strings, their current ordering and root artifact paths.
- Adopt only the adjudicated six technique CSV and twelve tactic JSON value changes; keep other catalog content stable.
- Keep unrelated untracked files untouched. Do not push, open a PR, or publish a release in this implementation.
- STIX/UUID adoption and unrelated catalog corrections are separate work.

## Review focus

1. YAML implicit scalar conversion, duplicate keys, anchors, aliases, and unknown tags must fail clearly.
2. A missing/extra/reordered ID or a filename/record mismatch must fail before output writes.
3. Existing reference defects must be visible and exact; new defects must fail.
4. All four outputs must be deterministic and `check` must catch any stale file.
5. A public-only fresh copy must build without sibling repositories or private credentials.

## Task 1: Strict V1 source loader

**Files:** `requirements.txt`, `ft3_tools/catalog.py`, `ft3_tools/__init__.py`, `tests/test_catalog.py`.

**Interfaces:** `load_catalog(root: Path) -> Catalog` returns ordered tactic and technique mappings; `CatalogError` reports source failures.

- [x] Write tests for strict YAML scalars, field sets, IDs, manifest bijection, malformed files, and known-reference regression behavior.
- [x] Run the tests and observe the expected failures.
- [x] Implement the minimal strict loader and validation; rerun focused tests.
- [x] Record exact existing reference exceptions in a V1-owned policy file; reject new or changed findings.

## Task 2: Import the catalog as YAML

**Files:** `catalog/order.yaml`, `catalog/tactics/*.yaml`, `catalog/techniques/*.yaml`, `docs/development/yaml-migration.md`.

**Interfaces:** One file per existing ID, retaining all V1 fields and strings. Tactic `domain` is `ft3`; the six corrected technique values match current JSON.

- [x] Generate the 149 YAML records and explicit order from the current V1 JSON arrays, applying only the adjudicated tactic-domain choice.
- [x] Run loader tests and a decoded field-by-field comparison against the original JSON, accounting for the twelve intentional domain changes.
- [x] Record original file hashes, the 18-cell disposition, and the source commit in the migration note.

## Task 3: Deterministic outputs

**Files:** `ft3_tools/export.py`, `ft3_tools/__main__.py`, `tests/test_export.py`, four root catalog files.

**Interfaces:** `render_catalog(catalog: Catalog) -> dict[str, bytes]`; `python3 -m ft3_tools check|build`.

- [x] Write failing tests for JSON/CSV byte conventions, exact initial parity, repeat rendering, stale outputs, and no writes on validation failure.
- [x] Implement in-memory generation and explicit build/check commands; rerun focused tests.
- [x] Regenerate the four root files and verify that only technique CSV and tactic JSON change, with exactly the adjudicated values.

## Task 4: Public workflow and final review

**Files:** `README.md`, `CONTRIBUTING.md`, `.github/workflows/catalog.yml`, `tests/test_portability.py`.

**Interfaces:** `python3 -m pip install -r requirements.txt`, `python3 -m unittest discover -s tests -v`, `python3 -m ft3_tools check`.

- [x] Add a fresh-copy test with only tracked public V1 files and no sibling repository.
- [x] Document YAML editing, output generation, the domain compatibility correction, and the deferred STIX scope.
- [x] Add CI to run the tests and read-only artifact check from the public checkout.
- [x] Run the full suite, artifact check, diff check, and independent adversarial review. Fix material findings and rerun their covering checks.
