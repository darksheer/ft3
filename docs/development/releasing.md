# Public FT3 V1 adoption check

This repository's YAML source, validator, and generated JSON/CSV outputs are sufficient to verify public V1 adoption. Publish the migration notice through the pull request and `yaml-migration.md`. The merged PR identifies the adopted commit; the migration document records the artifact hashes and compatibility changes. No release tag is required.

From the final candidate commit in a clean checkout, use an isolated Python 3.12 environment:

```sh
unset PYTHONPATH PYTHONHOME
export PYTHONNOUSERSITE=1
python3.12 -m venv .venv
PIP_CONFIG_FILE=/dev/null .venv/bin/python -m pip --isolated install \
  --index-url https://pypi.org/simple --no-cache-dir -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m ft3_tools check
git rev-parse HEAD
shasum -a 256 FT3_Tactics.json FT3_Techniques.json \
  'Fraud Tools Tactics and Techniques - FT3 - Tactics.csv' \
  'Fraud Tools Tactics and Techniques - FT3 - Techniques.csv'
```

Run `.venv/bin/python -m ft3_tools build` twice. After each build, require the hashes above to equal the committed artifact hashes, preserve file permissions, and require `git diff --exit-code` to show no tracked changes.

Record the upstream base and candidate SHAs, environment versions, verification results, and four hashes in the PR. Upstream `Catalog` CI must pass for that exact head and current base. Changes to either revision invalidate earlier acceptance evidence.

Stripe maintainers review and merge the PR. Until then, a verified ready PR is awaiting adoption. After observing the merge, repeat these checks from a fresh public checkout of the actual merged commit and confirm that upstream `master` contains it. A generated-file mismatch or an unreviewed change to the field contract or reference-exception policy blocks adoption.
