# FT3 Methodology

## Framing

FT3 is an intelligence-led living fraud taxonomy. F3 (MITRE's Fight
Fraud Framework) is a compatible high-level classification view.
The two layers serve different audiences and both are expected to
last.

Three load-bearing properties of FT3:

1. **Intelligence-led.** FT3's update rhythm is driven by adversary
   tradecraft observed in the wild, ingested through a pluggable
   adapter layer (Intel471, Feedly enterprise, CISA, ISAC feeds,
   vendor research, and anything added later). The maintenance
   pipeline is source-agnostic: adding a new intel source requires a
   configuration entry and an adapter, not a taxonomy rewrite.
2. **Living.** FT3 updates weekly from live intel. F3 updates on
   MITRE's biannual standards-track pace. The freshness delta is
   structural: F3 is *by design* slower because it is a standards
   artifact; FT3 is *by design* faster because it is operational
   intelligence. Both commitments are maintainable indefinitely.
3. **Compatible.** The F3 coverage view (`coverage/f3-coverage.html`
   and `.json`) surfaces every F3 ID alongside its FT3 coverage row.
   Anyone searching "does FT3 cover F3 technique X?" gets a clean
   answer — equivalent, derived, superset, subset, or unmapped —
   without needing to understand FT3's deeper structure. Boards,
   auditors, and CTID-aligned reviewers can read FT3 through the F3
   lens they already know.

The analogy stack: `FT3 : F3 :: ATT&CK : Kill Chain :: CWE : OWASP
Top 10`. In every pairing both layers survive, both serve different
audiences, and the operational layer updates faster than the
classification layer.

## Source-of-truth hierarchy

This repository publishes three layers, produced by a single
deterministic build pipeline:

- **Canonical edit sources** — `FT3_Techniques.json`,
  `FT3_Tactics.json`, and `crosswalk/crosswalk.json`. Humans and
  AI-augmented drafters propose changes to these via pull request
  against this repository; every change passes through a human
  review gate.
- **Canonical distribution artifact** — `stix/FT3_stix.json`. One
  STIX 2.1 bundle carrying every FT3 technique, tactic, sub-technique
  parentage relationship, F3 reference, ATT&CK reference, and native
  FT3 depth field. Downstream consumers read from this bundle.
- **Derived artifacts** — Navigator layers, MISP feed, F3 coverage
  view, and crosswalk CSV/XLSX exports. Each is regenerated from the
  STIX bundle alone by a deterministic script; no derivation reads
  the native FT3 JSONs directly. If a derived artifact cannot be
  satisfied from the bundle, the bundle is incomplete — that is the
  signal to fix.

## STIX identifier namespace

FT3 uses a project-minted UUIDv5 namespace for deterministic STIX
identifier generation.

- Namespace UUID: `5dc85083-7d0b-4566-a364-1588b3848449`
- Minted during Phase 0b on 2026-04-20
- Governance: write-once; this value must never be regenerated or
  changed
- Seed contract: `FT3:<id>`

Examples:

- `FT3:FT011.002` -> `519a87e8-b863-5ec9-bef1-8ed32c8d2a8c`
- `FT3:FTA001` -> `bb3898cb-2d16-5051-aaca-bb7b5229372f`

Anyone can verify an FT3 STIX identifier without reading this
repository's source: `uuid.uuid5(NAMESPACE, "FT3:<id>")` reproduces
the identifier exactly.

## STIX standards note

STIX 2.1 prefers UUIDv4 for SDOs, SROs, SMOs, and bundles, while
using UUIDv5 more explicitly for deterministic SCO identifiers. FT3
uses a project-owned UUIDv5 namespace as a documented project
policy so identifiers can be recomputed deterministically from the
published namespace and seed contract. This is a deliberate
deviation from the spec preference in exchange for reproducibility
and dedup across rebuilds — properties that are load-bearing for a
weekly-update cadence.

## STIX architecture — dual-encoded native fields

FT3 native depth fields (detection guidance, data sources, defenses
bypassed, detection strategy, per-record version, F3 mapping) have
no equivalent in the STIX 2.1 standard vocabulary. FT3 encodes them
in two places on every `attack-pattern` object:

1. As `x_ft3_*` top-level custom properties, matching the
   long-standing `x_mitre_*` convention used by MITRE ATT&CK and
   F3 itself. This maximizes interoperability with TIPs and tooling
   that already handle custom-property-style ecosystem extensions.
2. As a nested `property-extension` under the published
   `extension-definition` SDO (also shipped standalone as
   `stix/FT3_extension_definition.json`). This matches the 2025
   OASIS STIX Extension Definition Policy's preferred pattern for
   consumers that validate extensions against registered schemas.

FT3 does **not** use the older `toplevel-property-extension`
pattern, consistent with that policy.

## Consumer interoperability

### OpenCTI consumer note (2026-04-21 smoke, OpenCTI 7.260417.0)

OpenCTI's STIX 2.1 importer normalizes imported `attack-pattern`
objects against its own schema and does not preserve custom
`x_ft3_*` top-level properties; the `extension-definition` SDO
published for the `property-extension` pattern is also silently
dropped. Consumers reading FT3 via OpenCTI therefore see only the
FT3 ID (projected into `x_mitre_id` via the `mitre-ft3` external
reference), the `external_references` block (F3, ATT&CK, CAPEC,
CVE), `kill_chain_phases`, `name`, and `description`. For the
detection guidance, data sources, defenses bypassed, sub-technique
flag, and F3 relationship vocabulary, OpenCTI consumers should
resolve against `crosswalk/crosswalk.json` or the derived
`crosswalk/FT3-F3-crosswalk.csv` directly. OpenCTI's
name-based deduplication additionally collapses sub-technique
records that share a name with another record during import, so a
small number of `subtechnique-of` relationships do not survive
ingest.

Consumers not going through OpenCTI — direct STIX 2.1 readers,
MISP, MITRE ATT&CK Navigator — preserve the full bundle. See
`stix/FT3_stix.json` for the authoritative encoding.

### Other consumers

Navigator v17/v18/v19 layers render the full FT3 technique set.
MISP event objects carry FT3 ID + external references + description;
native depth fields do not map to MISP's event schema and are not
preserved via that path — consumers needing that depth read the
STIX bundle directly.

## 2024 content timeline

FT3 originated inside Stripe in 2024 as an internal fraud taxonomy
adaptation of ATT&CK-style structure. The enriched technique
records, tactic set, and crosswalk rows shipped in this repository
reflect that lineage. Per-record F3 mapping metadata — including
F3 numbering collisions that happen to share the sub-technique
suffix pattern — is captured honestly in `crosswalk/crosswalk.json`
and annotated in the `f3_mapping.numbering_collision` field. The
evidence is preserved for anyone who wants to trace it; the public
framing does not depend on it.

## License boundary

- FT3 is licensed under the MIT License (see `LICENSE.md`).
- F3 is published under Apache License, Version 2.0. F3-derived
  content carries the required NOTICE propagation in `NOTICE.md`;
  per-record attribution for every FT3 entry that references F3
  is enumerated in `ATTRIBUTION.md`.
- F3 identifiers are referenced as factual identifiers only. F3
  descriptive text is not embedded in this distribution; consumers
  retrieve F3 descriptions directly from F3's canonical bundle.
- MITRE ATT&CK identifiers are referenced as factual identifiers
  only per MITRE ATT&CK terms of use.
- Use of MITRE, ATT&CK, and F3 marks on this fork is nominative
  fair use for interoperability description. This repository is
  not affiliated with, sponsored by, or endorsed by The MITRE
  Corporation or the Center for Threat-Informed Defense.

## Maintenance and review

Weekly updates are drafted by AI-assisted pipelines running in a
private implementation repository and reach this public repository
as ordinary pull requests. Every pull request affecting the
canonical edit sources or published artifacts receives human
review before merge. Automation drafts; humans approve. The same
deterministic build pipeline regenerates every derived artifact
from the STIX bundle on every merge, and deterministic CI
workflows enforce byte-equality between the regenerated and
committed copies.
