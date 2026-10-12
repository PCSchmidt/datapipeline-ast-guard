# Results v2: severity and AG002 changes, re-measured on unseen repositories

Plan: [PROTOCOL_V2.md](PROTOCOL_V2.md), pushed before the changes were coded or any new file was collected, one deviation logged before the tool was run on the new files. Builds on [RESULTS.md](RESULTS.md). v1 (tag `v1-after-dev`) and v2 (tag `v2-frozen`) were each run **once** on corpus F: 288 files, 66,131 lines, 116 repositories with 20 to 500 stars, none used before.

> **Read this first.** One rater, who is also the author, labelled everything. F is a convenience sample of less famous repositories, many of them tutorials and course material. Findings cluster inside a few repositories (below), so the intervals, which treat findings as independent, are narrower than they should be. "Actionable" is a judgement call; I applied it uniformly but a different reviewer would draw the line elsewhere.

## What v2 changed (policy, not detection)

`AG001` is a warning, not critical. `AG002` reports an explicit cross join as critical in any file that imports a dataframe library, and a keyless `.join(other)` as a warning only in files that import `pyspark`. A `--fail-on {critical,warning,never}` option sets what makes the exit code 1. `AG001` and `AG003` detection logic is unchanged.

## 1. What the default gate does

| | v1 | v2 |
| --- | --- | --- |
| Files with any finding | 29.2% [23.4, 35.0] (84/288) | 28.5% [22.6, 34.4] (82/288) |
| Files that would **fail** the default gate (exit 1) | **20.8%** [16.0, 25.9] (60/288) | **2.1%** [0.4, 4.3] (6/288) |
| ...of which only because the file does not parse (`AG000`) | 6 files | 6 files |
| Files that fail for a real finding | 18.8% (54/288) | **0** |

v2 reports the same findings as before (112 `AG001`, 52 `AG003`, 6 `AG000`) and fewer `AG002` (3 under v1, 1 under v2). It stopped being a merge blocker because the severity changed, which is the whole effect: **the noise is not smaller, it is no longer blocking.** Intervals resample repositories. The six unparseable files are genuine syntax errors under Python 3 (one is Python 2 code), so `AG000` was right about them.

## 2. Are the findings right? (audited findings on F)

I labelled every `AG002` and `AG003` finding and a seeded random 60 of the 110 `AG001` findings. Both versions report the same `AG001` and `AG003` instances, so those rows are identical.

| Rule | Rule-faithful | Actionable |
| --- | --- | --- |
| `AG001` | 56/60 = **0.933** [0.841, 0.974] | 10/60 = **0.167** [0.093, 0.280] |
| `AG002`, v1 | 1/3 = 0.333 [0.061, 0.792] | 0/3 |
| `AG002`, v2 | 0/1 | 0/1 |
| `AG003` | 43/52 = **0.827** [0.703, 0.906] | 12/52 = **0.231** [0.137, 0.361] |

- **`AG003` did not hold at 0.94.** On unseen repositories rule-faithful precision is 0.83, which I had predicted (0.80 to 0.95, "lower than 0.94"). The earlier figure was measured on repositories whose errors I had just read. Nine of the 52 findings are not file-system paths: seven are AWS Systems Manager parameter names (`"/kafka_spark_demo/kafka_servers"`) from one repository, plus a REST route (`"/v1/capacities"`) and an API route constant. These are **a new mechanical false-alarm class that v1 and v2 share and that I did not fix**: strings that begin with `/dir/name` but are names or URL routes. The fix is obvious (skip strings passed as `Name=`, or ones that look like routes) but it belongs to a later version, not to this study.
- **`AG001` stays accurate and low-yield.** Rule-faithful 0.93; actionable 0.17, higher than the earlier 0.07 to 0.10, because F holds more "whole Spark or Polars frame converted to pandas to export or load" code (10 actionable findings). Those 10 come from only **5 repositories**; the four findings that are not rule-faithful are calls on an adapter object (`engine.to_pandas(...)`) or a frame sampled by a helper on the previous line. My earlier prediction of 0.03 to 0.20 held, with the previous estimate at the low end.
- **`AG002` found nothing real again.** v1 reported three findings: a pandas index `join` (rule-faithful by the rubric, harmless), a PySpark RDD key join (not a keyless DataFrame join) and a string join of a column list in a Polars file. v2 drops the first and third and keeps the RDD join. Under both versions, on 288 files, **no keyless or cross join was found in real code**, in line with the earlier 15 audited findings and one weak positive. This matches the expectation (fewer than 5 findings, zero or one rule-faithful).
- **Actionable `AG003` clusters.** 12 actionable findings come from 6 repositories, 6 from a single one (hard-coded home-directory paths in a course repository).

## 3. Regression checks (report only; nothing was changed)

- **Original corpus H, v2:** 73 of 300 files flagged (24.3%, v1 25.0%); 113 `AG001`, 51 `AG003`, 1 `AG002` (v1: 5), as expected.
- **Challenge set C, v2:** `AG001` and `AG003` unchanged from v1 (46/3/1 and 32/2/1). `AG002` falls to 21 right and 18 wrong against v1's 34 right. The 18 are an artefact of the harness: the snippets have no import lines, so v2 (correctly, by its own definition) has no evidence they are dataframe code. With one `import pyspark` line prepended to each `AG002` snippet, v2 matches v1 exactly (34 right, 5 wrong; the five are the documented known-hard cases). That supplementary run was not planned; I did it to separate the change in behaviour from the harness effect, and it did not change the tool.
- **Not covered:** `AG002` recall. The model-written corpus had no positives and F had none, so neither the cross-join nor the keyless branch has been shown to find a real defect.

## Against the expectations written in advance

| Expectation | Outcome |
| --- | --- |
| v1 `AG003` rule-faithful 0.80 to 0.95, below 0.94; actionable below 0.2 | **Rule-faithful yes (0.83, lower than 0.94). Actionable no: 0.23**, above the 0.2 I allowed |
| `AG001` rule-faithful above 0.9; actionable 0.03 to 0.2 | Yes (0.93; 0.17) |
| `AG002` under v2: fewer than 5 findings, zero or one rule-faithful | Yes (1 finding, 0) |
| Files failing the default gate: v1 roughly 10 to 20%, v2 below 3% | v2 yes (2.1%, all `AG000`). v1 slightly **above** my range (20.8%, interval to 25.9%) |
| v2 loses the challenge-set `AG002` cases written as positives | Yes, but because the snippets lack imports (see above) |

## What this does and does not show

- **Shown:** the severity change does what it was meant to: on code the tool has never seen, the default gate goes from failing about one file in five to failing none for a real finding. The earlier `AG003` precision was optimistic. `AG002` still has no demonstrated true positive.
- **Not shown:** recall; that the warnings are *worth* showing to engineers; that demoting `AG001` is correct for every team (teams that run pipelines on small drivers may still want `--fail-on warning`). The new `AG003` false-alarm class (parameter names and routes) is documented, not fixed.
- **Not claimed:** that v2 is a good linter. It is a better-behaved one, with its remaining weaknesses measured.

## Process notes and limits

1. Deviation 1 in the protocol: F has 288 files, not 300 (the Polars stratum is capped by the 3-per-repository rule).
2. The audit sample was drawn from the union of v1 and v2 findings so both versions are judged on the same instances; all `AG002` and `AG003` findings were labelled, 60 of 110 for `AG001`.
3. I applied one rule to ambiguous `AG003` findings: a hard-coded path or bucket in production-style code counts as actionable, a placeholder, a `/tmp` scratch path or an example does not, except persistent streaming checkpoints in `/tmp` and home-directory paths, which I counted as actionable. The labelling sheet is [corpus/labels_audit_fresh.json](../corpus/labels_audit_fresh.json) so it can be disputed finding by finding.
4. Limits as in the protocol: one rater who wrote the tool; findings cluster by repository (the 60 `AG001` and 52 `AG003` findings come from 29 and 22 repositories, with the largest repository contributing 7 and 11); F is a convenience sample.

## Reproduce

```bash
python scripts/collect_fresh.py                                          # clones; code stays local
python scripts/evaluate.py run --corpus fresh --split all --rules v1-after-dev --out results/fresh_v1-after-dev.json
python scripts/evaluate.py run --corpus fresh --split all --rules v2-frozen --out results/fresh_v2-frozen.json
python scripts/audit_fresh.py draw                                       # then label, then:
python scripts/score_fresh.py
```
