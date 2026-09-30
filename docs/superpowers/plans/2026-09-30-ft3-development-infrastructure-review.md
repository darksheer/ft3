# FT3 infrastructure plan adversarial review record

Planning date: 2026-09-30. Scope: production development infrastructure for the public Stripe FT3 V1 repository. Reviewers worked read-only with isolated initial context. No production code/catalog changes or upstream actions were performed.

## Expert use-case discovery

- infra_error_cases: gpt-6.1-sol, high effort. Defined parsing/schema/identity/Git/CLI/filesystem/export/CI error cases, expected 0/1/2 exits, read-only assertions and complete-run scenarios.
- infra_consumer_cases: gpt-6-astra, high effort. Independently probed prototype gaps and specified consumer/data/identity compatibility, bootstrap sequencing, exception ratchet and full-run acceptance.
- Coordinator: checked original field/header sets, all original date lexical representations, source byte sizes and original CSV terminators. Only planning documents were written.

## Round 1

Design SHA256: 84a5cb389a81f04ea790e569b7f16113ad144430756e6814886ae7d8e44d6ecf

Plan SHA256: 82f808f818bc7de16fdbabbb84e72bc8a8191173e715b4632aa168e23f039e1f

| Reviewer/model | Expertise | Verdict |
| --- | --- | --- |
| infra_plan_errors / gpt-6.1-sol high | Production errors, complete tests, filesystem safety, maintainability | REVISE |
| infra_plan_identity / gpt-6-astra high | Identity, contracts, consumer compatibility, bootstrap | REVISE |
| infra_plan_ci / gpt-5.6-sol high | Trusted CI/adoption, reproducibility, maintainer workflow | REVISE |

All findings were incorporated into the revised design and plan:

| Finding | Resolution in round 2 |
| --- | --- |
| Default publication could overwrite a destination created after the existence check | Atomic no-clobber publication; only explicit replace overwrites; full CLI concurrent-file/symlink tests |
| changes ambiguity contradicted complete-run exit contract | Explicit exit 2/completed:false, safe partial results and no inferred ambiguous additions/removals |
| Installed contract resources and selected-source exporter were underspecified | Packaged importlib.resources contracts, installed-wheel outside-repo run; selected JSON-only projection tests |
| Registry changes both required adoption and were expected to allow additions | Narrow exact new-record append allowed; missing/extra/retained-history changes fail |
| Prepared bootstrap fingerprints predated 31 parent edits | Separate historical assignment provenance and accepted bootstrap baseline; pure-UUID stage followed by corrections, or prior owner-reviewed fingerprint refresh preserving values |
| Row positions could make known-defect fingerprints unstable | Positions are display-only and excluded from canonical exception fingerprints |
| Required enforcement could block its own policy adoption | Explicit adoption-only expected non-passing receipt, authorized recorded maintainer adoption, accepted pin update, then separate catalog contribution |
| Hosted check-name/source and merge bindings were incomplete | Expected source/app/workflow and exact evaluated commit binding; spoof/fork/rebase/stale/merge/queue activation cases |
| Candidate data/Git environment/log payloads had no resource/injection acceptance | Exact resource/deadline budgets, controlled bare store and isolated tool, Git substitution/import and display-injection tests |
| Full-run evidence had no named durable receipt implementation | tests/record_runs.py, receipt.schema.json, artifact paths/digests and environment/action/lock provenance with clean-clone comparison |

## Round 2

Design SHA256: 65096b35de29aadf09b23bb556a3ddd449576f23e7a8352bce186ce6e2050e70

Plan SHA256: 04598ffc800e8440a58923c1b252c77f882cb789b82e2296b375dcf652888ceb

| Reviewer/model | Verdict | Evidence |
| --- | --- | --- |
| infra_plan_errors / gpt-6.1-sol high | APPROVED | Re-read complete revisions; no remaining Critical/Important error/test/maintainability planning finding |
| infra_plan_identity / gpt-6-astra high | APPROVED | Re-read complete revisions; independently verified 2838d3e minus UUID matches ee763e93 technique data and tactics unchanged |
| infra_plan_ci / gpt-5.6-sol high | APPROVED | Re-read complete revisions; adoption, check-source/SHA binding, trusted runner and reproducible receipts resolve prior findings |

Unanimous consensus reached in round 2: all three different-model reviewers approved the same exact design and plan hashes, with no remaining Critical/Important planning finding. Approval is only for these artifacts and readiness for human implementation approval. It does not certify unbuilt code, catalog correctness, owner adoption of policies, hosted enforcement activation or permission to publish/update Stripe PRs.
