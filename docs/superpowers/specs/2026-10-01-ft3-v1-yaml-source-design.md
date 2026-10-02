# FT3 V1 YAML source design

Status: accepted for local implementation by the 2026-10-01 conversation. It applies only to the public legacy FT3 repository.

## Purpose and boundary

Make one record per YAML file the editable FT3 V1 catalog. Generate the four existing root JSON/CSV files from that source so existing consumers retain their paths, identifiers, fields, string values, and record order. The build, tests, policies, and release instructions must work from this public repository alone. No private FT3 2.0 repository, schema, data, package, fixture, service, or governance decision is an input.

STIX is a later, independently specified projection. This change does not assign STIX IDs, infer detection objects, adopt UUIDs, retag techniques, or repair unrelated content.

## Authored data and contract

- `catalog/tactics/FTA###.yaml` and `catalog/techniques/FT###[.###].yaml` hold one mapping per record, using the current V1 field names and string values. The `id`/`ID` field must match its filename.
- `catalog/order.yaml` lists each tactic and technique ID exactly once in the current published order. Output order is explicit, not inferred from filenames.
- A V1-owned field contract fixes the existing nine tactic and 22 technique fields and their wire order. Unknown/missing fields, non-string values, duplicate keys/IDs, YAML aliases, anchors, merge keys, tags, and multiple YAML documents fail before export. A pinned public YAML parser is the only new runtime dependency.
- The parser preserves multiline text, whitespace, Unicode, empty strings, literal `TRUE`/`FALSE`, and date strings. It does not normalize or coerce authored values.
- Catalog checks enforce tactic-name uniqueness, technique ID grammar, flag versus ID shape, and references. Known existing reference defects are recorded as exact fingerprints; new or changed defects fail. This is a regression gate, not a claim that the legacy taxonomy is fully correct.

## Adjudicated source values

The merged V1 correction `a44c935` controls six technique conflicts: FT006 has `is_sub-technique: "FALSE"` and an empty `sub-technique of`; FT006.001, FT033.003, and FT033.004 have `is_sub-technique: "TRUE"`; 3DS Bypass has ID `FT056`. The 12 tactic `domain` values are `ft3`, a new catalog-wide policy choice based on agreement with tactic CSV and all technique records. Historical author intent for `fraud-attack` in tactic JSON is unproven; document the JSON compatibility change explicitly.

Only six technique CSV cells and twelve tactic JSON cells change at adoption. The other two root files remain byte-identical to the starting checkout. Parent-link defects outside these 18 conflicts remain separate work.

## Build and release contract

- A read-only `check` command regenerates all four artifacts in memory and fails on any byte difference. `build` validates the entire source and writes only the four generated root files; a failed validation writes none.
- JSON serialization preserves the current `indent=4`, ASCII escaping, field order, LF, and lack of terminal newline. CSV preserves the current header order, UTF-8, minimal quoting, CRLF records, embedded newlines, and lack of terminal record terminator.
- Document original and adopted artifact SHA-256 values plus the 18-cell disposition. Test the exact initial snapshot, deterministic repeat builds, malformed YAML, reference regressions, stale output detection, and a fresh public-checkout build without sibling repositories or private credentials.
- Contributors edit YAML and regenerate outputs. Any change to the contract, accepted known-defect policy, identity rule, or generated-file convention receives explicit review. A public release identifies its source commit and artifact hashes.

## Acceptance

The initial YAML catalog has 12 tactics and 137 techniques with unique IDs; all 149 generated JSON/CSV records agree field for field. Technique JSON and tactic CSV retain their original bytes. Technique CSV changes exactly the six adjudicated cells; tactic JSON changes exactly the twelve domain cells. Checks run from a clean copy containing only public V1 files. Existing unrelated worktree files remain untouched.
