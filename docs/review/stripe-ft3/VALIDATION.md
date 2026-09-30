# Reproducing the V1 contribution checks

Run from the integration evidence branch. All catalog checker inputs are Git blobs at the named revisions, not working-tree catalog files.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_catalog.py --base-ref 48f74e1b94815305e22c70a9ba8462738bbc6a26 --head-ref HEAD --findings docs/review/stripe-ft3/findings.csv --manifest docs/review/stripe-ft3/execution-manifest.json --identity-anchor-ref 7b7fc1a140235d1adb0f4a6ad21169d7753bed50
git -c core.whitespace=cr-at-eol diff --check 48f74e1b94815305e22c70a9ba8462738bbc6a26 HEAD
```

The identity anchor is the immutable reviewed revision containing the accepted initial assignment mapping and manifest. It is independent of upstream master, which predates UUID assignment. Do not replace it with a candidate revision to authorize reassignment.

`contribution_ready` means no introduced or undispositioned structural regression. `catalog_defect_free` remains false while disclosed baseline defects remain. Semantic findings in the review matrix/ledger require their stated follow-up decisions; the checker does not establish technical correctness of prose.

The standard-library checks need no installed dependencies. MISP schema validation used Python 3.12.13 and jsonschema 4.26.0 with the vendored schema pinned in the execution manifest. Reproduce with that dependency installed:

```sh
python3 -c "import json,jsonschema; jsonschema.validate(json.load(open('docs/review/stripe-ft3/misp-cluster-fixture.json')),json.load(open('docs/review/stripe-ft3/misp-cluster-schema.json')))"
```

Schema validation is not a live MISP import test. No claim is made about existing event attachments or rename behavior in an unspecified importer.
