# FT3 production development infrastructure implementation plan

> For agentic workers: use superpowers:executing-plans or superpowers:subagent-driven-development only after the user approves implementation. Steps use checkbox syntax. This document authorizes planning and review, not implementation or upstream writes.

**Goal:** Make V1 catalog development reproducible, compatible and safe through complete audits, trusted regression checks, portable tests, deterministic CSV projection and precise review reports.

**Architecture:** A small shared Python package separates contracts/parsing, catalog validation, trusted Git comparison, identity, export and reporting. Filesystem audits and Git comparison share rules but have separate trust and exit contracts. CI runs candidate-code tests; enforcement additionally requires a protected runner using accepted code and policy.

**Tech Stack:** Python standard library runtime and unittest; Python 3.11–3.14/Linux plus macOS 3.14 smoke tests; Git; hash-pinned development lint dependency and commit-pinned GitHub Actions.

**Spec:** docs/superpowers/specs/2026-09-30-ft3-development-infrastructure-design.md

## Global constraints

- Plan scope: public V1 only. Original upstream input is 48f74e1b94815305e22c70a9ba8462738bbc6a26; combined reviewed candidate is 4e5a4b5c7867ea42fea34ca2160403018daae8dc. Pin new execution inputs before implementation; never silently substitute moving refs.
- Preserve production catalog bytes during infrastructure work. No taxonomy/content/date/domain/UUID changes or CSV normalization in this cut.
- User's upstream hold covers all pushes, PR creation/updates/closures, issue writes and repository settings. Local commits may be prepared on an isolated codex/ branch after implementation approval.
- Preserve exact V1 fields, string types, ID/ID capitalization, optional blank strings, CSV field values and stored UUID assignments. No runtime dependency or network access is required to validate or test.
- Fixed counts apply only to frozen receipts; valid catalog additions must work. Technique and tactic deletion/renumbering and UUID reassignment are blocked. No generic transitions, merge/split/retirement or external UUID adoption in this cut.
- Exit 0 passes a complete run; exit 1 is a complete run with catalog/policy violations; exit 2 is invocation/decoding/filesystem/Git/trust/operational failure or ambiguous changes matching. audit/check-change decoded head violations return 1; changes with ambiguous identity returns 2/completed:false and safe partial results only. JSON reports always distinguish completion, pass and catalog cleanliness.
- Candidate input cannot redefine trusted policy, anchor, contracts or identity history. Hosted candidate-code CI is not an independent trust boundary.
- All final evidence must name tool/base/head/policy/input digests and remain reproducible from a fresh clone. No hardcoded workstation commit fixtures or shared object databases.
- Use readable typed Python, named dataclasses, small cohesive modules, explicit errors and stable rule identifiers. Avoid dense one-line code and broad silent exception handlers.

## Review focus

1. Invalid root/row/types must yield useful diagnostics without unsafe dependent checks or accidental success (Task 1/2).
2. A candidate changing both data and its expected policy/mapping must not authorize regeneration or exemption growth (Task 3).
3. Valid additions must pass while removal/renumbering of an unreferenced tactic remains blocked (Task 3/6).
4. CSV multiline/Unicode/newline fidelity and failed publication must preserve values and previous outputs (Task 4).
5. Fresh/shallow clone, missing Git objects and candidate-modified CI code must not rely on the developer environment or overstate trusted enforcement (Task 6/7).

## Planned files and public interfaces

Create pyproject.toml, requirements-dev.lock, ft3_tools/__init__.py, __main__.py, cli.py, models.py, contracts.py, loading.py, validation.py, git_inputs.py, policy.py, identity.py, export.py, changes.py and reporting.py. These are focused modules, not separate services. Use frozen dataclasses Diagnostic and RunReport for typed internal data; JSON serialization has schema_version:1 and structured values.

Create ft3_tools/resources/contracts/v1-legacy.json and v1-uuid.json as explicit declarative field contracts, not a partially implemented JSON-Schema interpreter; package them for importlib.resources loading. Create policy/known-defects.json and policy/identity-registry.json. Contracts fix all existing field names/order/types; identity profile and policy metadata must be bound to accepted inputs. Add tests/__init__.py so documented module-level test commands work.

Create tests/test_loading.py, test_validation.py, test_policy_identity.py, test_git_cli.py, test_export.py, test_changes.py, test_end_to_end.py, test_portability.py, helpers.py, record_runs.py and receipt.schema.json; fixtures contain synthetic representative catalogs plus small frozen excerpts/provenance. Full catalog scenario inputs are materialized from explicitly available source commits during local evidence runs, with hashes recorded; unit/integration tests do not require those commits.

Create .github/workflows/catalog-tests.yml and docs/development/{commands.md,trusted-runner.md,edge-cases.md}; update CONTRIBUTING.md and .gitignore. No unrelated README rewrite.

Public Python signatures:

- load_catalogs(root: Path, contract: CatalogContract) -> CatalogInputs
- validate(inputs: CatalogInputs, contract: CatalogContract) -> tuple[Diagnostic, ...]
- resolve_commit(repo: Path, full_sha: str) -> str; load_revision(repo: Path, sha: str) -> RevisionInputs
- compare(base: RevisionInputs, head: RevisionInputs, trusted: TrustedPolicy) -> RunReport
- project_csv(rows: Sequence[Mapping[str,str]], columns: Sequence[str]) -> bytes
- publish_csv(data: bytes, output: Path, replace: bool) -> None
- describe_changes(base: RevisionInputs, head: RevisionInputs, trusted: TrustedPolicy) -> ChangeReport
- serialize_report(report: RunReport|ChangeReport, format: str) -> str

Shared report fields and CLI behavior are defined in the spec. Consumers never call Git or publication from validation functions. Modules validate inputs before indexing/matching; duplicate identities are never silently overwritten.

## Task 1: Portable package, contracts, loaders and CLI failures

**Files:** package/CLI/models/contracts/loading; contract files; pyproject/lock; tests/test_loading.py and tests/helpers.py.
**Consumes:** Frozen existing field sets and CSV headers, supported Python versions, exit/report contract.
**Produces:** CatalogInputs, CatalogContract, Diagnostic, RunReport, strict loaders and callable CLI entry point.

- [ ] On an isolated local branch, record selected base SHA, source catalog hashes, exact original field/header lists and byte conventions. Derive contracts from actual inputs; review unknown-field/blank rules explicitly. No production data edits.
- [ ] Add named failing tests for missing/inaccessible files, invalid UTF-8, duplicate JSON keys, malformed JSON/CSV, object/null roots, null/list/string rows, missing/extra fields, incorrect wire types, missing/duplicate headers and wrong row widths. Use structured errors and no traceback assertions, not only exit codes.
- [ ] Run python3 -m unittest tests.test_loading -v and capture the intentional red result before implementing loaders/CLI.
- [ ] Implement strict UTF-8/duplicate-key decoding and CSV parsing; schema/type checks precede relation checks. Distinguish parse failures (2) from decoded contract violations (1); multiple independently readable catalogs still report their errors. Validate CLI argument combinations and JSON-mode operational reports.
- [ ] Implement the spec's exact input/resource limits and limit diagnostics. Add tests for oversized byte streams, nesting, field/row/diagnostic/report limits, invalid limits and supervised timeouts; every breach is exit 2/completed:false with no false success. Trusted Linux runner enforces 1 GiB memory budget; local macOS does not claim equivalent sandboxing.
- [ ] Pin the chosen lint tool exactly with installation hashes in requirements-dev.lock; record its official package provenance. Configure formatting/lint rules in pyproject.toml. Runtime/tests remain standard-library-only; no guessed action/dependency pins.
- [ ] Run loader suite and CLI invocation tests; verify missing arguments/outside-repo filesystem audit behavior and no input mutation. Commit this independently testable deliverable locally.
- [ ] Build/install a wheel from the clean source using locked build dependencies; run audit/export against fixtures from outside the repo. Assert contracts are included and cwd-independent. Preserve lock hashes for build/lint dependencies; no installation of candidate code occurs in the trusted comparison runner.

## Task 2: Complete snapshot validation and exact known-defect evidence

**Files:** validation.py, reporting.py, policy/known-defects.json; tests/test_validation.py; docs/development/edge-cases.md.
**Consumes:** Task 1 typed inputs/contracts; expert matrix below.
**Produces:** audit command, all structural diagnostics, exact canonical fingerprints and strict baseline receipts.

- [ ] Add failing tests for malformed/duplicate technique and tactic IDs; blank/duplicate tactic names; flag vocabulary; missing/conflicting/self/child parents; unknown tactics; complete field parity; impossible/lexically invalid dates and reversed chronology; missing/invalid/duplicate/wrong-version UUIDs under the required profile.
- [ ] Date tests cover technique 1/2/24 and tactic 01/02/2024, leap/non-leap days, unsupported widths/leading-zero technique formats, 00/68/69/99 explicit century behavior, trailing text and null. Do not guess chronology corrections.
- [ ] Run the validation suite red; implement the documented checks with stable rule IDs and deterministic diagnostic ordering. All collisions include affected positions. Parseable invalid rows must not crash later matching.
- [ ] Audit all four original catalogs and all four combined candidate catalogs in complete local runs. Capture exact diagnostics, schema/input hashes and counts. Independently derive exception fingerprints from each intended accepted baseline; never copy the prototype's broad ledger match as authorization.
- [ ] Keep strict audits failing while defects exist; expected candidate receipt contains exactly 25 diagnostics at the pinned source SHA. Original baseline's complete diagnostic set is mechanically derived and reviewed, not guessed. Separate schema-invalid, relation-invalid and unresolved content findings.
- [ ] Test reports for completed/pass/clean independence, stable bytes and structured expected/actual values. Exclude row positions from diagnostic fingerprints; reorder a known-defect record and assert its exception remains valid while display positions update. Commit validation and disclosed policy proposal locally; policy remains proposed until separately adopted.

## Task 3: Trusted Git comparison and identity protection

**Files:** git_inputs.py, policy.py, identity.py; policy registry; tests/test_policy_identity.py, tests/test_git_cli.py.
**Consumes:** Exact full base/head commits supplied by trusted runner; contracts/policy/profile/registry read exclusively from base; Task 2 diagnostics.
**Produces:** check-change command and explicit adoption-required diagnostics.

- [ ] Create tests using temporary git init repositories with base/head commits built within the test. Remove the prototype's hardcoded 7b/48f refs/shared clones entirely. Test valid SHA, absent objects, abbreviated/option-like/moving refs, missing catalog/policy paths, Git failure and unavailable required history; no fallback to filesystem or empty baseline.
- [ ] Test inherited GIT_* variables, local config/includes, replace refs, hooks/fsmonitor, promisor/alternate dependencies and import-path injection. Use scrubbed Git environment/raw blobs, no external filters/lazy fetch, accepted runner's own ordinary bare store, fixed 30-second subprocess and 120-second supervised CLI deadlines, and process cleanup. Reject unsupported object-store dependencies with exit 2.
- [ ] Add red tests for candidate-written exemptions, malformed/duplicate exception entries, changed/worsened/reintroduced defects, legitimate resolution, existing unresolved defect visibility, and an edit to working-tree manifest while Git blobs remain unchanged.
- [ ] Add red tests for tactic-ID replacement FTA004→FTA099 even when unreferenced; technique removal/renumbering; valid tactic/top-level/child additions; rename/reorder stability; duplicate names with distinct identities; UUID stripping/regeneration/reassignment/new UUIDv5; altered mapping/anchor/registry and attempted reuse of retained identities.
- [ ] Explicitly test fabricated transition triples, single/chained renumbering and merge/split/retirement requests are rejected as unsupported; this cut does not claim code-migration support. Valid head registry deltas contain exactly new catalog ID/UUID pairs with fresh UUIDv4s; missing/extra/unrelated additions or edits/omissions/reuse of retained entries fail. This narrow append is distinct from policy/bootstrap adoption.
- [ ] Run red suites, then implement resolved immutable inputs, exact exception comparison and trusted profiles. Missing/malformed trusted baseline prevents a complete comparison and returns 2. Head schema violations return 1 without unsafe identity matching.
- [ ] Implement bootstrap support only for a trusted base policy containing the prepared assignment registry and frozen fingerprints of the actual selected accepted legacy baseline. Preserve historical assignment provenance at ee763e93 separately. Check candidate stripped of UUID equals both base records and trusted fingerprints. Without prior adoption, bootstrap reports adoption_required and fails; mismatched trusted base fingerprints return 2, changed candidate non-UUID rows return 1. No --identity-anchor-ref or arbitrary code_transitions override is exposed.
- [ ] Full positive bootstrap: materialize the ee763e93 catalog plus independently selected trusted policy in a temporary test base, compare the UUID-stage 2838d3e data with the same 137 mapping values, then compare later parent corrections using the adopted UUID baseline. Changed mapping, input or candidate-written fingerprint refresh must fail. If actual rollout accepts parent edits first, require an earlier owner-reviewed trusted baseline refresh retaining all prepared values; the infrastructure implementer cannot adopt that refresh alone.
- [ ] Test two-stage adoption receipts and reject catalog changes sharing a policy/contract/bootstrap adoption change. A later candidate must use the earlier accepted revision; no unreviewed runner-pin update can authorize it. Local fixtures model external maintainer approval without performing any protected-repository write.
- [ ] Verify three full runs: valid contribution passes with disclosed unchanged defects; new defect plus self-exemption fails; complete candidate UUID/policy rewrite fails against the same accepted base. Record both data SHA and executed tool SHA. Commit locally.

## Task 4: Deterministic, safe single-file CSV export

**Files:** export.py/CLI command; tests/test_export.py; byte fixtures and provenance; commands documentation.
**Consumes:** Validated JSON projection fields and Task 1 contract/profile; explicit output path.
**Produces:** project_csv/publish_csv and read-only --check behavior.

- [ ] Freeze representative byte fixtures from both catalogs covering CRLF records, embedded LF, commas, doubled quotes, Unicode, empty cells, final empty columns and absent terminal newline. Test JSON key order independence and JSON row order preservation.
- [ ] Add red tests for byte-identical repeated generation, parsed value equality, stale check output, symlink/input-overlap destinations, missing destination parent, existing-output refusal, explicit replacement, unwritable output, injected short-write/disk-full/staging/replace failures and temporary-file cleanup. Full CLI race tests create a regular file or symlink after staging: normal mode returns 2, preserves external bytes and cleans staging.
- [ ] Implement pure projection with exact specified columns/dialect and no string normalization. Validate JSON structure/identity before publication; no edits to tracked CSVs. Current domain/parity conflicts remain audit/check failures, not hidden overrides.
- [ ] Load only selected JSON and contract: test absent/malformed current CSV and malformed unrelated catalog do not block projection. Stage complete bytes and round-trip validate. Normal mode uses atomic no-clobber linking; only --replace uses atomic replacement. Define permission preservation and publication-completed/durability-error reporting; do not promise pairwise atomicity, a hostile-filesystem sandbox or rollback after successful publication. Simulate failures without root/disk exhaustion.
- [ ] Run complete export→parse→audit→repeat→byte-compare scenarios for clean legacy and UUID fixtures. Generate original/candidate full projections only into temporary output; report differences from existing CSV honestly. Commit locally.

## Task 5: Reviewable change reports and consumer contracts

**Files:** changes.py, reporting.py; tests/test_changes.py; consumer fixtures.
**Consumes:** Resolved revisions/trusted contracts; validated IDs or adopted UUIDs; diagnostic deltas.
**Produces:** changes JSON/Markdown with exact before/after fields and compatibility summary.

- [ ] Add red tests for zero changes, valid additions, description/tactic/title edits, row reorder, header/field schema edits, UUID edits, duplicate-title records, ambiguous duplicate IDs, removal, introduced/resolved/unchanged diagnostics, and bootstrap transition requiring adoption.
- [ ] Implement identity-aware matching: FT IDs before UUID adoption, validated UUIDs afterward, plus explicit ID changes in the report. Never silently call a replaced concept a rename. Unsupported mutations remain visible even when the policy rejects them.
- [ ] Escape Markdown field content so multiline text/links/HTML cannot corrupt report structure; deterministic JSON preserves exact values. No rendering/evaluating content as commands. Include full catalog/tool/policy hashes and completion status; omit wall-clock values from deterministic payloads.
- [ ] Add ANSI/control/Unicode-control and ::workflow-command:: payload tests for text/Markdown/JSON and CI logging. Render display-safe text, preserve exact JSON-escaped values/fingerprints, and log only trusted summaries rather than raw candidate report strings.
- [ ] Test consumers reading by FT code, adopted UUID and original CSV headers/string values. Ensure two records with the same title remain distinct. No live MISP/STIX claim; retain schema fixture compatibility as optional, explicitly limited evidence.
- [ ] Add complete CLI tests for duplicate IDs, malformed IDs and duplicate UUIDs: changes exits 2/completed:false, retains safe diagnostics/partial fields, infers no ambiguous additions/removals, remains deterministic and makes no mutations. audit/check-change on decoded invalid heads still return 1. Run clean-fixture and mixed-invalid reports; verify repeated bytes and unchanged inputs. Commit locally.

## Task 6: Expert edge cases and complete system runs

**Files:** tests/test_end_to_end.py, tests/test_portability.py, tests/record_runs.py, tests/receipt.schema.json; docs/development/edge-cases.md; local outputs under artifacts/ft3-infra/<scenario>/.
**Consumes:** All commands and expert scenario matrix; exact frozen source inputs for local complete catalog runs.
**Produces:** Complete-run transcripts/structured receipts and traceable scenario→test mapping.

- [ ] Map every matrix row below to named tests, expected diagnostics/exits and mutation assertions. Record intentionally unsupported operations and human adoption boundaries; no case is marked covered solely by a unit test of a helper.
- [ ] Implement the named receipt generator/schema: scenario, exact argv/outcome, completion/pass, expected outcome, tool/base/head/policy/contract/catalog/lock and output digests, OS/image/Python/Git/action provenance. Separate environment metadata from deterministic payloads. Test clean-clone payload regeneration byte equality while environment differences are disclosed; raw artifacts are ignored and a final local acceptance manifest binds paths/digests.
- [ ] Full Run A: strict audit all original and combined candidate records; confirm original defects visible and candidate's known 25 diagnostics; validate both legacy and UUID profile selection from trusted policy.
- [ ] Full Run B: clean synthetic catalog→audit→export both outputs separately→parse→parity audit→change report→repeat byte compare; exercise names, Unicode, multiline/quotes, empty optional fields and two same-title records.
- [ ] Full Run C: valid tactic/technique/child additions plus ordinary prose edit and reorder pass trusted comparison; all old IDs/UUIDs preserved and precise additions reported. No 137/12 production ceiling.
- [ ] Full Run D: multi-error head reports all safe independent defects in one invocation with exit 1; parse/Git/filesystem/resource/timeout failures report incomplete exit 2; candidate control/ANSI/workflow strings are safely displayed; before/after inputs and Git status unchanged.
- [ ] Full Run E: bulk UUID regeneration, mapping/profile/anchor/exemption/registry rewrites, unreferenced tactic replacement and field removal fail against the same trusted base; policy rewrite never earns an exemption.
- [ ] Full Run F: exception ratchet—preserve, fix, worsen, introduce and reintroduce defects; only preserved approved defects and genuine repair pass. A promised fix remaining is an explicit failure.
- [ ] Full Run G: fresh clone and file:// --depth 1 clone of an ephemeral test repo, with no alternate object DB/workstation SHAs. Entire suite runs; a missing requested base fails 2, explicit baseline fetch then permits complete comparison. Hostile Git environment/config/replace refs and candidate import injection cannot alter accepted inputs/code; resource timeouts clean child processes. Candidate executable code is never invoked by trusted comparison.
- [ ] Full Run H: export filesystem failures and concurrently created files/symlinks preserve prior/external output before publication and leave no temporary files; repeated success is deterministic. Installed-package runs from outside repo resolve contracts. Run on Linux and macOS; fault-inject critical paths consistently.
- [ ] Run lint and complete unittest discovery on supported Python versions; direct supported entry point discovers all tests. Require an offline test run after dependencies are installed. Complete subprocess timeouts and child cleanup tests.
- [ ] Inspect unexpected failures and add the exact regression scenario before correcting code. No coverage-percentage-only claim; every scenario must have executable evidence. Commit complete local evidence and scenario index.

## Task 7: CI, protected runner handoff and contributor workflow

**Files:** .github/workflows/catalog-tests.yml; docs/development/commands.md and trusted-runner.md; CONTRIBUTING.md, .gitignore.
**Consumes:** Portable full suite; validated CLI contract; runtime matrix.
**Produces:** Candidate test workflow, exact fresh-checkout commands, and a separate enforcing-runner adoption checklist/procedure.

- [ ] Add/document commands: install locked development dependencies; lint; python3 -m unittest discover -s tests -v; audit; check-change with exact SHAs; export --check; changes. Provide expected failing strict-audit behavior on current known defects. Fix the repository issue link and remove misleading commented test TODOs.
- [ ] Pin third-party actions to verified complete commit SHAs, use read-only contents permission, persist-credentials:false, no secrets/write tokens or publishing, and a bounded timeout. Candidate tests run on pull_request/push with unprivileged permissions; platform/version matrix follows spec.
- [ ] Run hosted-equivalent commands in a fresh local clone before considering CI configured. Use only tracked fixtures and locked dependencies; workflow artifact reports contain exact candidate and tool SHA.
- [ ] Document/enact locally the trusted runner: install a verified accepted-tool wheel in an isolated environment, fetch candidate catalogs as inert blobs, select accepted base externally, execute python -I -m ft3_tools against immutable candidate SHA from outside candidate checkout, output report. Disable environment/cwd import influence and Git external hooks/config execution. Do not execute candidate modules/hooks/configs/dependency install or workflows in this gate.
- [ ] Separate initial adoption and later enforcement: base master has no tools yet, so first infra adoption needs independent full-run/human review. Before any hosted gate is claimed enforcing, maintainer must validate protected code provenance, exact head-SHA status binding, required-check/merge behavior and fork execution. If those cannot be demonstrated, report local infrastructure ready and hosted enforcement pending; do not invent a privileged workflow workaround.
- [ ] Document the adoption-only path: no production catalog-byte changes, non-passing adoption-required receipt, named maintainers independently approve exact digests, separately authorized one-time protection bypass or protected pin update with audit record, accepted runner pin updated only after acceptance, later catalog contribution based on that earlier revision. This is a handoff procedure; user hold prohibits executing it here.
- [ ] Hosted activation cases: candidate uses trusted check name, fork PR, rebase/new head, stale prior-head receipt, synthetic merge commit and merge queue if enabled. Require recorded evidence that source/app/workflow and exact evaluated commit are bound by protection; check-name equality alone is insufficient. Unsupported activation remains pending. Preserve hosted receipts with 30-day artifact retention and local download before expiry.
- [ ] Add acceptance tests/fixtures for runner selecting a manipulated candidate checker and prove it still executes accepted code. Document trusted runner reference-update review; policy/contract/identity adoption needs an independent earlier accepted revision.
- [ ] Commit locally. Keep every upstream action on hold; provide exact reviewable artifacts instead of publishing.

## Task 8: Final production acceptance and adversarial implementation review

- [ ] Record immutable final base/head/tool/policy/contract hashes. Run the complete unit/integration/portable/consumer/export suite, strict audits, trusted comparison, change report and CRLF-aware git diff --check against these exact inputs.
- [ ] Have independent specialists review error contracts, consumer compatibility and trust/CI behavior. Different model versions challenge the same exact implementation SHA; return findings with concrete reproductions. Fix every Critical/Important defect and repeat affected full runs plus the final gate.
- [ ] Deliver readiness separately: infrastructure tests; no introduced catalog regression; disclosed catalog defects; policy/schema/UUID adoption; hosted enforcement activation; unverified MISP integration. Each has evidence or an explicit pending decision.
- [ ] Handoff a clean local branch and evidence. Request implementation-result review before any upstream publication; never interpret plan approval as PR/push approval.

## Expert-defined edge-case matrix

These are implementation acceptance cases, not claims that code exists. Expert sources: infra_error_cases (gpt-6.1-sol/high) and infra_consumer_cases (gpt-6-astra/high), independent read-only consultation on 2026-09-30.

| Cases | Expected behavior | Owning task/full run |
| --- | --- | --- |
| Missing file, permissions, directory, UTF-8/JSON/CSV syntax, duplicate JSON keys | Exit 2, clear path/position, completed:false, no mutation | 1/D |
| Root/row wrong type; missing/extra/unknown key; null/number/bool where string required | Exit 1, complete safe diagnostics, dependent checks skipped | 1–2/D |
| Missing/duplicate/reordered/extra header, blank row, wrong width | Parsed contract failure 1; lexical malformed CSV 2; reorder export mismatch explicit | 1–2/B/D |
| Blank/malformed/duplicate IDs in both namespaces; blank/ambiguous tactic names | Exit 1, all conflicting positions; no overwritten identity dictionaries | 2/D |
| Parent missing/self/child/wrong prefix, inconsistent flag, unknown tactic | Exit 1; do not infer taxonomy correction | 2/A/D |
| Exact calendar grammar/pivot, leap day, reversed chronology, null dates | Exit 1 for decoded violations; no crash/date rewrite | 2/A/D |
| Shared field removed in both formats; JSON/CSV record/field mismatch | Exit 1 despite parity of edited formats | 2–3/E |
| Candidate exemption/policy/profile/anchor rewrite; stale/duplicate/worsened/reintroduced defects | No self-authorization; trusted ratchet or adoption-required failure | 3/E/F |
| Unreferenced tactic replacement, technique deletion/renumbering, unsupported migration chain | Exit 1 and exact unsupported operation | 3/C/E |
| Valid new tactic, parent/child, rename/prose/tactic changes, row reorder | Pass with all existing identities preserved; no count ceiling | 3/C |
| UUID missing/duplicate/noncanonical/v5/new collision/regeneration/reassignment/retained reuse; exact/missing/extra/altered registry append | Exit 1 under trusted required profile; exact valid append passes, no bootstrap self-blessing | 3/C/E |
| Pure UUID bootstrap, later parent edits, stale frozen input, candidate fingerprint refresh | Prepared values preserved; only prior trusted baseline adoption permits bootstrap | 3/E |
| Duplicate titles and code/UUID lookups | Distinct records retained, complete deterministic change summary | 3/5/B/C |
| Missing/ambiguous/moving/option-like refs, missing paths/objects/base, branch changes midrun | Reject non-full SHA; exit 2/no fallback; input snapshots fixed | 3/G |
| Oversized/nested inputs, too many rows/fields/diagnostics/report bytes, slow/hung subprocess | Exact versioned limits; exit 2/completed:false; cleanup and no partial success | 1/3/D/G |
| Hostile GIT_* environment/config/replace refs, candidate import injection, promisor/alternate stores | Accepted controlled store/code; no substitutions/external execution/lazy fetch | 3/G |
| Commas, quotes, CR/LF, Unicode, whitespace, optional blanks, final empty columns | Exact value round-trip; deterministic wire bytes | 4/B/H |
| Existing/symlink/overlapping/unwritable output, disk/write/replace failures; concurrent file/symlink after staging | Exit 2; atomic no-clobber without --replace, preserve external bytes and clean staging | 4/H |
| Stale export and repeated export | Exit 1 check mismatch; repeat identical bytes/no check writes | 4/B/H |
| Partial/unstable reports, embedded Markdown/HTML/newlines; duplicate/malformed identity in changes | Ambiguous changes exits 2/completed:false, no inferred ambiguous records; stable escaped data | 5/D |
| ANSI/control/Unicode controls/workflow command strings | Display-safe text/Markdown/logs; exact JSON-escaped values and unchanged fingerprints | 5/D |
| Local object/commit dependence, shallow history, no network test run | Full portable suite passes; missing comparison base fails clearly | 6/G |
| Candidate-edited checker/workflow, check-name spoof, fork/rebase/stale head/merge commit/queue | Accepted source plus exact evaluated SHA binding; otherwise enforcement pending | 7/G |
| Adoption-only/mixed adoption+catalog, unreviewed pin change | Two-stage authorized handoff; mixed/self-authorized changes cannot pass | 3/7/E/G |

## Plan review and consensus procedure

Planning stages: expert case discovery → written design/plan → coordinator self-review → three independent adversarial model reviewers → revisions/resubmission to the same reviewers until unanimous approval of the same artifact hash. Reviewers: gpt-6.1-sol, gpt-6-astra and gpt-5.6-sol, each high effort with isolated initial context. Expertise: production error/testing, catalog identity/consumer compatibility, CI/trust/maintainer rollout. Initial reviews are independent; reviewers receive other findings only in revision rounds to challenge their resolution. No majority vote or automatic approval after a fixed number of rounds. If reviewers disagree on a material owner decision, retain it explicitly and seek that decision rather than claiming consensus.

Record exact artifact SHA256 digests, model/version, round, findings and dispositions, unresolved limits and each verdict in docs/superpowers/plans/2026-09-30-ft3-development-infrastructure-review.md. Approval means the plan is ready for human implementation approval; it does not mean code exists or all source catalog defects are resolved.

## Coordinator self-review

- Contracts/profiles and trust baseline are explicit; every prototype flaw identified by both experts is assigned to a test/task.
- Error cases distinguish parsing from parsed invalid data and prevent crashes/silent baseline fallbacks.
- Counts do not freeze growth; tactic IDs and every known field are protected.
- Export is one file per publication, current line endings are retained, domain conflicts remain disclosed and unmodified.
- Initial policy/UUID/CI adoption is explicit; no candidate self-approval or upstream authorization is inferred.
- Whole-run coverage includes clean, current, invalid, malicious, filesystem, Git, portability and consumer cases.
- Generic migrations and live consumer integrations are explicitly unsupported; their tests fail honestly rather than promise unimplemented behavior.
