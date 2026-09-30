# Stripe FT3 issue remediation implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task. Steps use checkbox syntax. This is a proposed plan; no catalog edits, UUID assignments, external comments, or PRs have been made in this planning pass.

**Goal:** Address every item in Stripe FT3 issues #1–#4 with upstream-reviewable PRs, and review the complete V1 catalog for omissions before declaring the work ready.

**Architecture:** Correct Stripe's existing JSON and CSV catalogs directly. Preserve public technique codes and record identity; add stored opaque technique UUIDs without adopting the separate V2 catalog's schema. Keep independent changes in independent PRs and check their combined result.

**Tech stack:** Existing JSON/CSV files, Python standard library for catalog checks, Git and GitHub CLI; MISP's official cluster schema for a compatibility fixture.

**Spec:** The user's request of 2026-09-29, the complete bodies and comments of [#1](https://github.com/stripe/ft3/issues/1), [#2](https://github.com/stripe/ft3/issues/2), [#3](https://github.com/stripe/ft3/issues/3), and [#4](https://github.com/stripe/ft3/issues/4), plus the concrete design decisions below. Decisions requiring maintainer acceptance are identified explicitly.

## Global constraints

- Baseline inspected: Stripe master `48f74e1b94815305e22c70a9ba8462738bbc6a26`; refresh upstream before implementation.
- 137 techniques, including 81 subtechniques; 12 tactics. No deletion, code reuse, renumbering, or silent merging in the four issue PRs.
- Changes apply to Stripe V1. V2 fixes alone do not satisfy the upstream reports.
- Preserve all unrelated fields, record order, CSV quoting and record terminators. JSON/CSV parity is checked by identity, not row position alone.
- There is no tracked STIX artifact or exporter in this repository. Do not add a full STIX or MISP exporter to solve these issues.
- Keep `id` and `stix_id` distinct from the proposed bare `uuid` field. Do not put a bare UUID into `stix_id`.
- Use `Refs #N` for issue PRs, without closing keywords. Only Stripe maintainers decide issue closure.
- Existing reviewed local commits are separate branches: `3c18ea5` (VPS), `a9376af` (date docs), `ba56e7d` (CSV parity). Do not assume any one contains the others.
- PR descriptions include the problem, exact behavior change, compatibility implications, and verification evidence. Comply with Stripe's contribution/CLA process.
- Local implementation and validation do not wait for Stripe to accept a schema or tooling proposal. Present additive UUID/schema changes in a reviewable PR; Stripe's adoption decision occurs on that concrete contribution. Do not contact the requester without explicit authorization.
- Preserve the original three commit refs. Record refreshed upstream SHA, each contribution base/head SHA, and the ordered integration commit list in `docs/review/stripe-ft3/execution-manifest.json`.

## Review focus

1. Duplicate names and the historical FT053 collision must not collapse UUID assignments.
2. Social-media acquisition, compromise, impersonation, and victim phishing must remain distinguishable, including every neighbor named in issue #2's comment.
3. Rename, code correction, row reorder, and repeated export must preserve committed UUIDs; uniqueness alone cannot prove persistence.
4. Documentation must describe the dates actually present after combined changes, including 2026 edits, without inventing historical dates or implying valid chronology.
5. Independently valid PRs must remain valid together: no dropped branch changes, CSV header divergence, mistaken parents, or obsolete README examples.

## Task 1: Restore technique CSV parity with merged PR #5

**Files:** `Fraud Tools Tactics and Techniques - FT3 - Techniques.csv`.

**Consumes:** Master JSON, already corrected by [PR #5](https://github.com/stripe/ft3/pull/5).
**Produces:** Matching technique JSON/CSV, with no semantic edits.

- [ ] Rebase or replay `ba56e7d` onto refreshed upstream; inspect rather than regenerate the entire CSV.
- [ ] Correct six cells: FT006 flag and parent; FT006.001 flag; FT033.003 and FT033.004 flags; 3DS Bypass's code from FT053 to FT056.
- [ ] Parse both formats and assert 137 records, unique codes, exact equality for all 22 shared fields, preserved order, and no unrelated cell changes. Confirm FT053 still means Card Holder Details Collection and owns its three children.
- [ ] Run `git -c core.whitespace=cr-at-eol diff --check`; retain byte/CSV round-trip evidence for existing multiline quoting and CRLF record boundaries.
- [ ] Commit and create a parity PR referencing PR #5. This is a prerequisite for UUID initialization and the combined final gate.

## Task 2: Resolve issue #1's VPS acquisition distinction

**Files:** `FT3_Techniques.json`; corresponding technique CSV.
**Consumes:** Existing FT007.005 and FT007.007 identities and reviewed commit `3c18ea5`.
**Produces:** Two distinct acquisition methods with matching descriptions and detection.

- [ ] Replay the existing patch on its own branch; retain FT007.005 and FT007.007.
- [ ] Name FT007.005 `Acquire Access: Hijacked VPS`: unauthorized control of an existing instance/account through credentials or exploitation.
- [ ] Name FT007.007 `Acquire Access: Rented VPS`: provisioning/rental with stolen payment information. Remove takeover examples from this record and payment-rental examples from the hijacking record.
- [ ] Keep shared downstream uses, but distinguish takeover authentication/management evidence from signup/payment/provisioning evidence. A VPS IP, phishing host, or C2 signal alone proves neither acquisition method.
- [ ] Verify both target rows match across all fields, only approved fields changed, IDs/count/order remain stable, and unrelated data is unchanged. Reuse the existing independent validator and review evidence after adapting its baseline to refreshed master.
- [ ] Record modification dates appropriate to the actual accepted edits; validate formatting. Existing wrong parent links remain explicitly tracked under Task 6 rather than silently repaired here.
- [ ] Commit and create PR with `Refs #1`.

## Task 3: Resolve issue #2, including both named neighbor records

**Files:** Technique JSON/CSV; a short scope note in `README.md` if prose fields cannot express the boundaries clearly.
**Consumes:** FT018, FT021, FT007.010, FT008.003; current tactic catalog.
**Produces:** A before/after scope matrix and a PR that removes confusing overlap without deleting identities.

- [ ] Review complete descriptions, examples, detection, tactic placement, and parent links for all four records. Issue #2's comment explicitly includes FT007.010 and FT008.003; reviewing only FT018/FT021 is insufficient.
- [ ] Proposed scope: FT018 `Social Media Phishing for Initial Access` covers victim-facing lures for credentials/session access or malicious-content execution. FT021 `Social Media Impersonation` covers deceptive presentation as a trusted person/brand. FT007.010 covers obtaining social accounts/access as resources; FT008.003 covers unauthorized takeover of an existing social account.
- [ ] Explicitly separate purchased access from direct compromise, and acquisition of an account from subsequent use of that account to impersonate or phish. Explain that a chain can involve several techniques without making them synonyms.
- [ ] Inventory every original behavior clause across the four records and disposition it as retained, reassigned to an identified record, or removed with a source-backed rationale. Include personal-data collection, malicious-file execution, misinformation, harassment/doxxing, defamatory content, reputation effects, and stock manipulation. Broad or unsupported claims need not survive, but no behavior may disappear without a recorded reason. Verify detection and examples against this inventory.
- [ ] Review FT021's current `Defense Evasion & Obfuscation` placement against the selected scope. Document a justified existing-tactic choice; do not silently copy V2 tactic labels or automatically change every social record to Initial Access.
- [ ] Use [MITRE T1566.003](https://attack.mitre.org/techniques/T1566/003/) and [T1656](https://attack.mitre.org/techniques/T1656/) as behavior references, and review establish/compromise-account neighbors. Do not blindly backport V2's credential-only narrowing, which would omit the original malicious-file branch.
- [ ] Present literal proposed text and the four-record boundary matrix for content review before applying it. If faithful differentiation proves impossible, document a merge alternative with preserved legacy identities/lineage; do not improvise deletion.
- [ ] Require a named owner decision for any materially new concept or merge/replacement alternative; keep that affected task pending rather than preserving an old identity by fiat. Ordinary clarification that retains a concept proceeds under the accepted issue design and records its rationale. UUID bootstrap cannot proceed on unresolved concept identity.
- [ ] Verify retained malicious-link/file examples, matching JSON/CSV, unchanged public IDs/count, correct detection for each behavior, and preserved unrelated records. Update modification dates only for edited records.
- [ ] Commit and create PR with `Refs #2`; include the four-record scope matrix and any tactic decision in its description.

## Task 4: Resolve issue #4's format question without a breaking date migration

**Files:** `README.md` only for the issue PR.
**Consumes:** Existing date values and reviewed commit `a9376af`.
**Produces:** Accurate documentation of both catalog formats and parsing examples.

- [ ] Replay the existing README patch: techniques use month/day/two-digit-year; tactics use zero-padded month/day/four-digit-year. Both are calendar dates with no time or timezone, and neither is an ISO timestamp.
- [ ] Scan JSON and CSV values to verify examples and document the actual two-digit years present. The prior patch mentions only 24/25; combined VPS/social edits introduce 26, so update that sentence before submission or integration.
- [ ] Provide an unambiguous example per catalog. Restrict century interpretation to the current data rather than inventing an ongoing pivot rule.
- [ ] Verify all catalog data blobs are unchanged by this PR, README links resolve, and `git diff --check` passes.
- [ ] Explicitly distinguish the format answer from Task 6's chronology anomalies. Offer ISO normalization as a separate compatibility migration only if Stripe requests it.
- [ ] Commit and create PR with `Refs #4`.

## Task 5: Resolve issue #3 with persistent per-technique UUIDs

**Files:** Technique JSON/CSV; UUID policy in `README.md`; unconditional local validator `scripts/check_catalog.py`, tests `tests/test_catalog.py`, and evidence under `docs/review/stripe-ft3/`. Upstream inclusion of the tooling/evidence is separately reviewable and does not gate producing it locally.
**Consumes:** Unique repaired V1 codes and the selected semantic snapshot from Tasks 1–3.
**Produces:** A stored `uuid` on all 137 records, mirrored exactly in CSV, with preservation checks.

- [ ] Before assignment, check for any published mapping from the intended MISP integrator. Inspect public evidence; if no mapping is available, record that limit. Contacting the requester is a separate explicitly authorized action, not part of this planning pass.
- [ ] Proposed choice: assign UUIDv4 once per existing concept and commit it. Preserve any verified existing downstream mapping, or document an explicit persistent crosswalk if it cannot be adopted. Document the additive CSV header/schema compatibility change in the concrete PR rather than waiting for advance upstream acceptance. If no public mapping is available, proceed with first-party assignments and state that independently published/private mappings were not reconciled; do not claim universal downstream continuity.
- [ ] Document JSON as authoritative for UUID assignments and CSV as its matching projection. Preserve existing codes and leave `stix_id` untouched. V2 UUIDv5 identifiers are a separate identity system, not an automatic V1 assignment source.
- [ ] Freeze the selected pre-assignment input SHA and SHA256 fingerprints of every record in `docs/review/stripe-ft3/uuid-bootstrap-input.json`. Define a fingerprint as SHA256 of UTF-8 canonical JSON (`sort_keys=True`, compact separators, `ensure_ascii=False`) containing the complete pre-UUID record. Bootstrap refuses changed fingerprints, duplicate codes, mismatched JSON/CSV, unexpected counts, and ambiguous historical FT053 input. FT056 and FT053 receive distinct identities. Never use title alone as the lookup key.
- [ ] Add checks for canonical syntax, RFC variant/version 4 for newly assigned UUIDs, nonblank coverage, uniqueness, exact JSON/CSV equality, and no changes to existing non-UUID fields. Preserve adopted external mappings according to their explicitly documented version rules.
- [ ] Commit the initial mapping in `docs/review/stripe-ft3/uuid-initial-assignments.json`, recording UUID, initial FT code, concept description/fingerprint, and bootstrap input SHA. Record its Git blob ID and commit SHA in the execution manifest. Treat that initial mapping as immutable; compare later assignments both to that fixed blob and to a named previous reviewed revision. Do not allow replacing fixtures/current baselines in the same patch to bless regenerated UUIDs.
- [ ] Validate persistence: title edits, code correction with an explicit transition mapping, row reorder, repeat runs, and re-export retain the same UUID. Reject wholesale regeneration, duplicate claims, changed initial mappings, and disappearance without an explicit lifecycle disposition. New concepts receive new identities; retired UUIDs are never reused. Future legitimate additions or transitions require a separate reviewed mapping change, not rewriting the initial snapshot.
- [ ] Define how future merge/split/supersession retains retired identities before any retirement occurs. Do not bundle a merge or a full lifecycle subsystem into initial assignment.
- [ ] Build a small MISP cluster fixture using the FT3 UUID as `values[].uuid` and validate against a pinned [official cluster schema](https://github.com/MISP/misp-galaxy/blob/main/schema_clusters.json). Header/galaxy UUIDs identify separate objects.
- [ ] State validation limits: schema acceptance is not proof of rename-safe imports or preservation of existing event attachments. Test those against a pinned converter/importer and existing MISP state before claiming end-to-end integration; otherwise disclose them as unverified.
- [ ] Commit and create PR with `Refs #3`; include policy, audited mapping, regression results, and downstream compatibility limits.

## Task 6: Our own catalog review and follow-up disposition

This planning pass performed structural/date/parity checks over every row and targeted semantic review of issue-related records. It is not an exhaustive technical-correctness audit of all descriptions. The following findings are confirmed at baseline; fixes remain proposed and should have their own reviewable PRs.

| Finding | Evidence | Planned treatment |
| --- | --- | --- |
| Technique CSV lags merged JSON | Six unequal cells; duplicate FT053 remains in CSV | Task 1 |
| Parent fields conflict with code prefix or are blank | 33 of 81 subtechniques: four FT004 children point to nonexistent FT0004; three children have blank parents; 26 point to another existing technique | Review each intended parent using names/descriptions, then repair JSON/CSV in a hierarchy PR; do not renumber IDs or blindly trust the prefix |
| Tactic references do not resolve | FT027 and FT027.001/.002/.003 use `Discovery & Profiling`, absent from the 12-tactic catalog | Compare the existing Reconnaissance and Execution definitions; propose explicit reclassification or a separately justified missing tactic, without inventing IDs |
| Tactics disagree across formats | All 12 JSON domains are `fraud-attack`; CSV domains are `ft3` | Determine intended domain using upstream context and consumer expectations; propose one consistent value in a parity PR |
| Modification predates creation | FT033.003; FT051.001/.002/.003/.004 | Seek provenance/history. Do not set guessed creation dates or automatically clamp timestamps; repair only with evidence or document unresolved provenance |
| Exact duplicate titles | FT023/FT035; FT037/FT042; FT037.003/FT042.002 | Review meaning and tactic boundaries before renaming or merging. Dispute Avoidance also warrants checking whether prose describes adversarial abuse or legitimate customer service |

- [ ] Produce `docs/review/stripe-ft3/catalog-review.csv` with exactly one row for each of the 137 techniques and 12 tactics from the reviewed input snapshot. Columns: `catalog`, `id`, `input_sha`, `scope_verdict`, `tactic_verdict`, `parent_verdict`, `description_examples_verdict`, `detection_verdict`, `overlap_ids`, `finding_ids`, `source_urls`, `rationale`, `reviewer`. Use `not_applicable` explicitly for tactic-only/non-parent fields. No unchecked row counts as reviewed.
- [ ] Review all tactic definitions against referenced technique behaviors and identify missing/unused categories without assuming every unused tactic is a defect.
- [ ] Classify each finding as confirmed defect, intentional distinction, or unresolved content question. For overlaps, record both differences and shared behaviors; similarity alone is not a merge decision.
- [ ] Record every finding in `docs/review/stripe-ft3/findings.csv` with `finding_id`, affected IDs, evidence, severity/impact, disposition (`fix_in_pr`, `intentional`, `deferred_provenance`, `needs_owner_decision`), rationale, linked task/PR or next action, and reviewer. Reconcile all matrix finding references with this ledger.
- [ ] Review proposed edits against the complete issue text and comments and the combined diff. Keep unrelated corrections separate from issue PRs.
- [ ] Build and run local `scripts/check_catalog.py` and `tests/test_catalog.py` unconditionally. Checker interface: `python3 scripts/check_catalog.py --base-ref <reviewed-base-sha> --head-ref <reviewed-head-sha> --findings docs/review/stripe-ft3/findings.csv --manifest docs/review/stripe-ft3/execution-manifest.json`. It reads Git blobs at the supplied refs; checks counts/uniqueness, reference resolution, flags, JSON/CSV parity, date parsing/chronology, and UUID persistence when UUIDs exist; emits every defect and exits nonzero on introduced regressions or undispositioned failures. Existing defects are reported with matching ledger dispositions, not suppressed. Use `python3 -m unittest discover -s tests -v` for regressions.
- [ ] Include regression cases for missing/duplicate records, malformed CSV/multiline quoting, wrong parent/tactic, mismatched fields, invalid/reversed dates, distinct UUIDs for duplicate titles, rename/reorder/re-export preservation, deliberate code transitions, and attempted baseline replacement/UUID regeneration. A checker with dispositioned defects passes only contribution-readiness; it must label the catalog as having remaining defects.
- [ ] If Stripe declines tooling in a PR, retain the exact scripts, fixtures, pinned dependency/schema versions, commands, and results as separately accessible review evidence. No validation claim depends on untracked scripts available only in another local worktree.
- [ ] Keep unknown historical dates/content questions as named outstanding items. A proposed PR is not proof they were resolved.

## Task 7: Combined verification and upstream handoff

- [ ] Use independent branches from refreshed upstream for CSV parity, #1, #2, and #4. Stage #3 after Tasks 1–3 are merged; if review can proceed before merge, build it on their explicit ordered integration snapshot, publish it as a dependent draft PR, and record the predecessor PRs/commits. Rebase to Stripe master and reverify once those predecessors land. Use one branch/worktree per PR; never present a stacked diff as an independent UUID-only change.
- [ ] Build an integration checkout containing every proposed fix. Check the final JSON/CSV catalogs, not only isolated diffs. Confirm no local patch was dropped and the README describes the resulting dates and UUID behavior.
- [ ] Verify counts, unchanged/explicitly mapped identities, exact field equality, parent and tactic references, flags, valid dates, and chronological dispositions. Validate CSV byte/round-trip stability and whitespace with existing CRLF conventions.
- [ ] Review the full combined change as a consumer: lookup by FT code, lookup by UUID, CSV import, title changes, and expected MISP mapping. Record unavailable consumer tests rather than calling them passed.
- [ ] Include fresh test transcripts and review results with each PR. Recheck live issue/PR state and diff after publication.
- [ ] Deliver links to every submitted PR and a coverage matrix listing addressed requirements, dependencies, unresolved review findings, and maintainer decisions. Leave all upstream issue closures to Stripe.

## Readiness rules

- **Plan ready:** all adversarial reviewers approve the same plan revision; design alternatives requiring human content decisions are explicit task gates, not assumed answers.
- **Scoped PR ready:** all its issue requirements are covered; no unresolved identity/scope decision affects its edits; its local checks and regression tests pass; remaining pre-existing catalog findings are disclosed with specific dispositions. An unrelated provenance-dependent date anomaly may remain open without blocking a VPS clarification PR.
- **Review complete:** every input technique/tactic has a reviewed matrix row, every finding has evidence and a disposition/next action, and the combined proposed changes have been checked. `needs_owner_decision` affecting a proposed edit blocks that edit/PR, while separately scoped audit questions remain explicitly outstanding.
- **All catalog defects resolved:** every confirmed defect is repaired and verified, and every content/identity question is decided. Do not use this label while historical anomalies, accepted deferrals, or substantive questions remain. PR submission or a contribution-readiness pass is not a claim that Stripe merged anything or that the catalog is defect-free.

## Plan self-review, 2026-09-29

- All four issues are mapped to tasks, including both additional social-account records named in issue #2's comment.
- The additional CSV parity fix is included and sequenced before UUID initialization.
- UUID generation and persistent identity are distinguished; no MISP importer success is inferred from a schema check.
- Date format documentation is separated from provenance-dependent chronology repairs.
- Existing local review artifacts can be reused as evidence, but rebasing and combined changes require fresh verification.
- No tracked STIX artifact was found; the plan contains no unnecessary STIX-export work.
- The broader review is explicitly unfinished until Task 6's complete semantic review and finding dispositions are delivered.
