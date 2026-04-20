# FT3 Methodology

## STIX identifier namespace

FT3 uses a project-minted UUIDv5 namespace for deterministic STIX identifier
generation.

- Namespace UUID: `5dc85083-7d0b-4566-a364-1588b3848449`
- Minted during Phase 0b on 2026-04-20
- Governance: write-once; this value must never be regenerated or changed
- Seed contract: `FT3:<id>`

Examples:

- `FT3:FT011.002` -> `519a87e8-b863-5ec9-bef1-8ed32c8d2a8c`
- `FT3:FTA001` -> `bb3898cb-2d16-5051-aaca-bb7b5229372f`

## STIX standards note

STIX 2.1 prefers UUIDv4 for SDOs, SROs, SMOs, and bundles, while using UUIDv5
more explicitly for deterministic SCO identifiers. FT3 uses a project-owned
UUIDv5 namespace as a documented project policy so identifiers can be
recomputed deterministically from the published namespace and seed contract.
