# Public FT3 V1 release check

This repository's YAML source, validator, and generated JSON/CSV outputs are sufficient to prepare a public V1 release. No other repository or private fixture is an input.

From the reviewed release commit in a clean checkout:

```sh
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 -m ft3_tools check
git rev-parse HEAD
shasum -a 256 FT3_Tactics.json FT3_Techniques.json \
  'Fraud Tools Tactics and Techniques - FT3 - Tactics.csv' \
  'Fraud Tools Tactics and Techniques - FT3 - Techniques.csv'
```

Record the commit, four hashes, and consumer-facing value changes in the release notes. A maintainer can then tag and publish the reviewed commit through the public repository's normal release process. A mismatch in the generated-file check or an unreviewed change to the field contract or reference-exception policy blocks the release. This document does not itself publish or tag anything.
