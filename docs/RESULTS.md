# Results

**No benchmark has been run yet.** Nothing here is a claim about detection quality.

## Planned measurement (not done)

| Item | Protocol |
|---|---|
| Corpus | 200+ LLM-generated PySpark/Polars scripts, each hand-labelled for AG001-AG003 ground truth, split dev/test before rules are tuned |
| Metrics | per-rule precision and recall, false-positive rate on known-good production-style code, runtime per 1k LOC |
| Report | confusion table per rule, list of misses (e.g. limit applied on an earlier statement) |

## Verified today

- 10 tests pass, including a hypothesis test that arbitrary text never raises and a regression test for string/path joins.
- `mypy --strict` and `ruff` clean.
- SARIF output has the 2.1.0 structure and correct 1-based line/column.

## Development finding

While writing the README I tested `", ".join(names)` and found AG002 flagged it as a keyless DataFrame join (critical, so it would block CI). Fixed for string-literal receivers, `os.path.join` and list/generator arguments, with a regression test. `sep.join(parts)` is still flagged because it cannot be told from a DataFrame join without type information. This is the kind of false positive the planned labelled corpus is meant to measure; it was found by inspection, not by measurement.
