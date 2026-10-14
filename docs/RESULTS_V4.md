# Results v4: closing the AG003 false-alarm kinds, and a fourth unseen sample

Plan: [PROTOCOL_V4.md](PROTOCOL_V4.md), committed before the code this time, with two deviations logged before the tool was run on the new sample. v3 (tag `v3-frozen`) and v4 (tag `v4-frozen`) were each run **once** on corpus F3: 300 files, 88,107 lines, 133 repositories created since 2024-01-01 with 5 to 500 stars, none cloned for H, F or F2 (570 repositories excluded). Builds on [RESULTS_V3.md](RESULTS_V3.md).

> **Read this first.** One rater, who is also the tool's author. F3 is a convenience sample of newer, small repositories dominated by configuration-heavy Spark and Docker projects; findings cluster inside a few repositories (the three largest supplied 19 of the 59 audited findings), so the intervals (which treat findings as independent) are optimistic.

## What changed in v4

`AG003` no longer reports a string constant that is an argument of a regular-expression call (`re.compile(...)`), the first argument of an experiment-tracking call (`mlflow.set_experiment(...)`), anywhere inside the value of a `Name=` or `SecretId=` keyword, or an argument of a string method (`replace`, `split`, `strip` and similar). `AG001` and `AG002` are unchanged. Each exclusion has a regression test that also asserts that a neighbouring real path is still reported (28 tests).

## 1. Effect of the change

| Corpus | v3 findings | v4 findings | What v4 removed |
| --- | --- | --- | --- |
| F2 (223 files; where the four kinds were found) | 115 | 109 | exactly 6 `AG003` findings: 2 experiment names, 3 regular expressions, 1 `replace("s3://", "")`. All six were labelled not-a-path in the v3 audit |
| F (288 files) | 160 | 160 | nothing |
| H (300 files) | 165 | 165 | nothing |
| **F3 (300 files, fresh)** | **238** | **238** | **nothing**: the four kinds do not occur |

So v4 does what it was designed to do and is inert elsewhere. The F2 result is not independent evidence (the rules were designed from those six examples); F3 is the check, and F3 contains none of the four kinds.

## 2. `AG003` on F3 (v3 and v4 report the same 59 findings, all audited)

| | Result |
| --- | --- |
| Rule-faithful precision | **59/59 = 1.000** [0.939, 1.000], from 24 repositories |
| Actionable precision | 13/59 = **0.220** [0.134, 0.341], from 7 repositories |
| False-alarm kinds found | **none** |

- **No new false-alarm kinds appeared.** Every one of the 59 findings is an absolute path or a listed URI scheme used as a path in code: Spark configuration (`spark.home`, jar and class paths), checkpoint and warehouse locations, container paths such as `/app/config.yaml`, Databricks mount points, buckets in f-strings, and Windows or home-directory paths. My pre-stated expectation that at least two new kinds would appear was wrong.
- **A precision of 1.0 is not a claim that the rule is perfect.** The earlier samples showed 0.83 to 0.90 with different kinds of code; F3 happens to be dominated by Spark configuration strings, which the rule's definition counts as paths. A different sample would likely reveal another kind. What the four samples together say is that the false-alarm rate is sample-dependent and the kinds are many but not unbounded.
- **Actionable precision is stable at about one in five** (0.22 here, 0.15 on F2, 0.23 on F). The actionable ones are Databricks mount points written straight into read and write calls (five from one repository), hard-coded buckets and checkpoint locations in module constants, and Windows or home-directory paths from a developer's machine.
- **`AG002` reports its first true, explicit cross join on real code.** (Earlier rule-faithful cases were a pandas index join, no longer reported since v2, and a cross join emulated with a constant key.) In F3 the only `AG002` finding is an explicit `left_df.join(right_df, how="cross")` inside a function whose purpose, documented in its docstring, is a cartesian product. It is a true cross join and not worth a reviewer's time (labelled actionable: no). Across the four studies (H, F, F2, F3), the only true cross or keyless DataFrame join that v2 and later report was this intended one.

## Against the expectations written in advance

| Expectation | Outcome |
| --- | --- |
| Every instance v4 removes is not rule-faithful, at most one exception | Yes on F2 (6 of 6 not-a-path); nothing removed on F3, so no further test |
| v4 minus v3 precision between 0 and +0.03 | Yes, exactly 0 on F3 (nothing differs) |
| At least two new false-alarm kinds in F3 | **Wrong:** none |
| v3 rule-faithful precision on F3 between 0.75 and 0.92 | **Wrong:** 1.000 |
| Actionable precision below 0.25 | Yes (0.22) |
| v4 changes at most 8 findings across F, F2 and H, all false alarms | Yes (6, all false alarms) |

## What this does and does not show

- **Shown:** the four kinds found in the v3 audit are closed without removing anything else on four corpora; on a fourth unseen sample of newer repositories `AG003` had no false alarms; the exclusion-list approach has not needed a new entry on F3.
- **Not shown:** that the list is complete. The prediction that every sample would reveal new kinds failed on F3, but F3 is a particular population; a Java-style or SQL-heavy or notebook-export sample might differ. Recall in the wild and the value of the warnings to engineers are still unmeasured.
- **Not claimed:** that `AG003` is a good gate. It remains a warning that is right about what it matches nearly always and worth a look about one time in five.

## Process notes and limits

1. Deviations 1 and 2 (protocol): `gh search` cannot sort by creation date, so F3 was defined by a creation-date filter (created on or after 2025-06-01), which gave only 25 files, so it was widened to creation on or after 2024-01-01 with 5 to 500 stars. Both changes were made before the tool was run on F3.
2. `AG001` is unchanged and was not relabelled (174 findings, 91 files flagged of 300: 30.3%).
3. F3's four unparseable files were counted as `AG000`.
4. Limits as in the protocol: one rater who wrote the tool; clustering by repository; the exclusions designed from six examples.

## Reproduce

```bash
python scripts/collect_fresh3.py                       # clones; code stays local
python scripts/evaluate.py run --corpus fresh3 --split all --rules v3-frozen --out results/fresh3_v3-frozen.json
python scripts/evaluate.py run --corpus fresh3 --split all --rules v4-frozen --out results/fresh3_v4-frozen.json
python scripts/audit_fresh3.py draw                    # then label, then:
python scripts/score_fresh3.py
```
