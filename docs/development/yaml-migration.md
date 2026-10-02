# FT3 V1 YAML migration record

The source snapshot is public V1 commit `48f74e1b94815305e22c70a9ba8462738bbc6a26`. The four catalog files had these SHA-256 hashes before and after migration:

| File | Before SHA-256 | Adopted SHA-256 |
| --- | --- | --- |
| `FT3_Tactics.json` | `3585420ff8ff18e5ef8354aa9f9f6052913415e96d42b1b6d58260bfb687f422` | `71515ae149bb6ea5fcb113637c445c49c7eedb130d9ba311acecbc26cfbe5671` |
| `FT3_Techniques.json` | `c1bb6fe3c8eb6726dfa34cc99a3418c78505183bd3c12b8a322742a7ae5bd0f0` | `c1bb6fe3c8eb6726dfa34cc99a3418c78505183bd3c12b8a322742a7ae5bd0f0` |
| `Fraud Tools Tactics and Techniques - FT3 - Tactics.csv` | `a7cc2107dd4526da62d9e05b2eb95691f0957220b40c7f44191166458956963f` | `a7cc2107dd4526da62d9e05b2eb95691f0957220b40c7f44191166458956963f` |
| `Fraud Tools Tactics and Techniques - FT3 - Techniques.csv` | `68e857e2fae75ee8eccc255afa5f8deb8a828a9d9ca5b71fd86ee6b1bde34434` | `526657f2ae24b04eea201bca5791095689e223933a485b7222c6be2eea4efb58` |

The 137 technique YAML records were imported from `FT3_Techniques.json` without changing values. The 12 tactic YAML records were imported from `FT3_Tactics.json` with their `domain` value set to `ft3`. Record order and all field names, scalar strings, and text whitespace were preserved. The import used only files in this public V1 repository.

## Adjudication of the 18 JSON/CSV disagreements

| Record(s) | Field | Canonical YAML value | Published artifact changed |
| --- | --- | --- | --- |
| FT006 | `is_sub-technique` | `FALSE` | Technique CSV |
| FT006 | `sub-technique of` | empty string | Technique CSV |
| FT006.001 | `is_sub-technique` | `TRUE` | Technique CSV |
| FT033.003, FT033.004 | `is_sub-technique` | `TRUE` each | Technique CSV |
| 3DS Bypass | `id` | `FT056` | Technique CSV |
| FTA001–FTA012 | `domain` | `ft3` each | Tactic JSON |

The six technique values follow the merged correction commit `a44c935c28802e114269335f34dc2ba0718df6df`; CSV still held its earlier values. The tactic domain choice is a new V1 policy decision: all technique JSON/CSV records and all tactic CSV records already used `ft3`. The original commit held `fraud-attack` only in tactic JSON. We cannot prove its author's intent from repository history, so the changed tactic JSON value is an explicit consumer compatibility change.

The source still has 37 known reference defects: four records cite the absent `Discovery & Profiling` tactic, four use the absent parent `FT0004`, three dotted IDs have an empty parent, and 26 dotted IDs cite a different existing parent from their own ID prefix. `catalog/reference-exceptions.json` records those exact findings. This migration does not repair them. New or changed reference findings fail validation.

Run `python3 -m ft3_tools check` after editing YAML. The four root JSON/CSV files are generated outputs; changes to them should come from `python3 -m ft3_tools build` and be reviewed with the YAML diff. STIX and UUID adoption are outside this migration.

No public release was cut by this migration work. At release time, record the tagged commit (`git rev-parse HEAD`) with these adopted artifact hashes, using the public-only procedure in `releasing.md`.
