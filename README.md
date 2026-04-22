# FT3 — Fraud Tools, Tactics & Techniques

FT3 is an intelligence-led living fraud taxonomy — 137 techniques
across 12 tactics, updated weekly from real-world adversary
tradecraft. It is F3-compatible: every F3 technique resolves to a
first-class FT3 coverage view, so anyone asking "does FT3 cover F3
technique X?" gets a clean, authoritative answer. FT3 preserves
the operational-layer depth practitioners need — detection
guidance, data sources, defenses bypassed, and per-procedure
attribution — while fully referencing the F3 classification layer
above it.

## What this repository ships

This fork of `stripe/ft3` publishes the canonical edit sources
alongside generated distribution artifacts for the broader
ecosystem. Everything below derives from three canonical JSON
edit sources (`FT3_Techniques.json`, `FT3_Tactics.json`,
`crosswalk/crosswalk.json`) via a single deterministic build
pipeline run from the private implementation repo.

| Layer | File | Purpose |
|-------|------|---------|
| Edit | `FT3_Techniques.json` | 137 enriched technique records with FT3 identity fields, F3 crosswalk, ATT&CK lineage |
| Edit | `FT3_Tactics.json` | 12 tactic records with FT3 identity fields + F3 mapping |
| Edit | `crosswalk/crosswalk.json` | Authoritative FT3↔F3 row-level crosswalk (234 rows covering both directions) |
| Distribution | `stix/FT3_stix.json` | Canonical STIX 2.1 bundle (234 objects) — the one input for every derived consumer artifact |
| Distribution | `stix/FT3_extension_definition.json` | Standalone STIX extension-definition for strict consumers |
| Derived | `navigator/FT3_navigator.attack-17-1.json` · `attack-18-1.json` | ATT&CK Navigator overlay layers for ATT&CK Enterprise 17.1 and 18.1 |
| Derived | `misp/FT3_misp_feed.json` + per-event files | MISP-compatible feed for TIPs that import by URL |
| Derived | `coverage/f3-coverage.html` · `.json` | F3 coverage view — every F3 ID with its FT3 coverage row (or the "no FT3 coverage yet" state) |
| Derived | `matrix/FT3_matrix.html` · `.json` | Native FT3 12-tactic matrix view |
| Derived | `crosswalk/FT3-F3-crosswalk.csv` · `.xlsx` | Consumer-facing crosswalk exports |

## Downloads & direct links

Every asset listed above is attached to the matching GitHub
release and is available in this repository tree. SHA-256
checksums for each asset are published in release notes so
consumers can verify integrity.

Three FT3 visualizations answer three distinct audience
questions — one artifact each:

| Question | Artifact | Direct link |
|---|---|---|
| What does the FT3 matrix look like? | `matrix/FT3_matrix.html` | [open matrix](https://raw.githack.com/darksheer/ft3/master/matrix/FT3_matrix.html) |
| Does FT3 cover F3 technique X? | `coverage/f3-coverage.html` | [open F3 coverage](https://raw.githack.com/darksheer/ft3/master/coverage/f3-coverage.html) |
| What ATT&CK techniques does FT3 cover? | `navigator/FT3_navigator.attack-18-1.json` | [open in ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fraw.githubusercontent.com%2Fdarksheer%2Fft3%2Fmaster%2Fnavigator%2FFT3_navigator.attack-18-1.json) |

GitHub serves `raw.githubusercontent.com` with
`Content-Type: text/plain` for security reasons, so HTML
artifacts don't render directly from the raw URL. The
`raw.githack.com` proxy serves the same files with
`Content-Type: text/html` so browsers render them; release
assets are also downloadable if a local copy is preferred.

For TIPs and practitioner tooling:

- **STIX 2.1 readers** — consume `stix/FT3_stix.json` directly.
  FT3 native depth fields are dual-encoded as `x_ft3_*` top-level
  properties AND a nested `property-extension` under the
  published `extension-definition` SDO. See
  `docs/METHODOLOGY.md` for the consumer interoperability notes.
- **MITRE ATT&CK Navigator** — open one of the overlay layers
  directly in the hosted Navigator:
  - [ATT&CK 18.1 overlay](https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fraw.githubusercontent.com%2Fdarksheer%2Fft3%2Fmaster%2Fnavigator%2FFT3_navigator.attack-18-1.json)
  - [ATT&CK 17.1 overlay](https://mitre-attack.github.io/attack-navigator/#layerURL=https%3A%2F%2Fraw.githubusercontent.com%2Fdarksheer%2Fft3%2Fmaster%2Fnavigator%2FFT3_navigator.attack-17-1.json)

  Each layer highlights the ATT&CK techniques an FT3 record
  references in its `attack_references`. FT3-native techniques
  without ATT&CK lineage do not appear in the Navigator overlay
  by design — the hosted Navigator domain enum does not support
  custom domains. For the full native FT3 matrix, use
  `matrix/FT3_matrix.html` above. See `docs/METHODOLOGY.md` for
  the schema rationale.
- **MISP** — import the feed at `misp/FT3_misp_feed.json` via
  MISP's URL-import path; per-event JSON files accompany the
  manifest.
- **Board / executive reporting** — open
  `coverage/f3-coverage.html` via the direct link above for the
  F3 lens (every F3 ID with its FT3 coverage status).

## Operating rhythm

F3 updates on MITRE pace (biannual). FT3 updates weekly from live
intel sources ingested through a pluggable adapter layer. The
freshness delta is a structural property of how the two
frameworks are maintained — F3 is a standards artifact; FT3 is
operational intelligence. Both serve different audiences and both
are expected to last.

## AI-augmented maintenance

Routine drift detection, semantic re-mapping, and triage over
intel-feed ingestion are produced by LLM-assisted pipelines
running in the private implementation repository. Every change
that reaches the public FT3 JSONs or published artifacts passes
through a human review gate — no taxonomy edit merges without
explicit reviewer approval. Automation drafts; humans approve.

## License boundary

- FT3 is published under the MIT License (see `LICENSE.md`).
- F3-derived references carry Apache 2.0 NOTICE propagation per
  `NOTICE.md`; per-record attribution is enumerated in
  `ATTRIBUTION.md`.
- F3 identifiers (F####, F####.NNN, TA####) are referenced as
  factual identifiers only. F3 descriptive text is not embedded
  in this distribution; consumers retrieve F3 descriptions from
  F3's canonical bundle at
  `raw.githubusercontent.com/center-for-threat-informed-defense/fight-fraud-framework/refs/heads/main/public/f3-stix.json`
  directly.
- MITRE ATT&CK identifiers (T####) are referenced as factual
  identifiers only per MITRE ATT&CK terms of use. The use of
  MITRE, ATT&CK, and F3 marks on this fork is nominative fair
  use for interoperability description; this repository is not
  affiliated with, sponsored by, or endorsed by The MITRE
  Corporation or the Center for Threat-Informed Defense.

## Components of FT3

### Tactics
High-level categories representing phases or goals within the
fraud lifecycle. Each tactic delineates specific objectives
pursued by adversaries.

Example: **Initial Access** — obtaining unauthorized access to
user accounts to execute fraudulent transactions.

### Techniques
Methods or modes of operation adversaries use to achieve their
objectives under each tactic. Techniques vary in complexity and
sophistication.

Example: **Account Takeover** — using compromised credentials to
gain control over a user's account for malicious purposes, such
as transferring funds or making unauthorized purchases.

### Procedures
Specific implementations of techniques that detail the exact
methods actors use within the context of fraud, often involving
unique tools and sequences of actions.

Example: **Phishing Scheme** — crafting a fake email that
appears legitimate to trick users into providing their login
information.

### Indicators of Compromise (IOCs)
Details that suggest fraudulent activity, such as unusual
transaction patterns or changes in account behavior.

Example: **Unusual Purchase Locations** — transactions occurring
in locations that do not match the user's typical behavior.

### Mitigations
Proactive actions organizations can adopt to decrease the risk
or impact of fraud.

Example: **Two-Factor Authentication (2FA)** — extra security
layers that require a second form of verification to access
accounts.

### Detection
Mechanisms for identifying potential fraud through analysis of
transaction patterns and customer behaviors.

Example: **Anomaly Detection Algorithms** — machine-learning
models that identify deviations from normal purchasing behavior.

### Response
Predefined procedures for organizational response to detected
fraud events, aimed at minimizing impact and facilitating
recovery.

Example: **Fraud Investigation Protocol** — steps for initiating
a fraud investigation when suspicious transactions are flagged.

## Contributing

Contributions to the FT3 framework are welcome. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## Security

See [`SECURITY.md`](SECURITY.md).

## Code of Conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Contact

For inquiries about the FT3 framework, reach out via the
repository issue tracker.

## Notice

See [`LICENSE.md`](LICENSE.md), [`NOTICE.md`](NOTICE.md),
[`ATTRIBUTION.md`](ATTRIBUTION.md),
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md),
[`CONTRIBUTING.md`](CONTRIBUTING.md), and
[`SECURITY.md`](SECURITY.md) for details.

Original FT3 © 2024 Stripe Inc. This fork maintained by
Darksheer Labs; see `LICENSE.md` for MIT terms.
