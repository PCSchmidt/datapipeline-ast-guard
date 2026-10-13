# Protocol v3: a fix for the AG003 route/parameter-name false alarms, and a first measure of recall by mutation (written before the changes were coded, before any new file was collected and before the tool was run on it)

Follows [PROTOCOL_V2.md](PROTOCOL_V2.md) and [RESULTS_V2.md](RESULTS_V2.md). v2 left two things open: `AG003` precision on unseen code was 0.83, with a new false-alarm class (AWS Systems Manager parameter names such as `Name="/app/servers"`, and REST routes such as `session.get("/v1/capacities")`) that I did not fix; and recall on real code has never been measured, because real code contains almost no true `AG002` cases and labelling every file is not affordable. This protocol fixes the first and measures the second by **mutation**: inject a known defect into real code and check whether the tool finds it.

## What changes in v3 (decided now from the v2 audit; no other rule logic changes)

`AG003` stops reporting a string constant when it is:

1. the value of a keyword argument named `Name` or `SecretId` (the boto3 spelling for parameter and secret identifiers), or
2. the first positional argument of a call to a method named `get`, `post`, `put`, `delete`, `patch` or `head` and starts with `/` (an HTTP route or a mapping key, not a data path), or
3. a string that begins with `/api/` or `/v` followed by digits and `/` (an API version prefix).

Scheme URIs (`s3://...`), Windows drive paths and every other absolute path are still reported. `AG001` and `AG002` are unchanged. Each exclusion gets a regression test that also asserts a neighbouring real path is still reported. v3 is frozen and tagged `v3-frozen` **before** the new sample is analysed.

## Questions

1. Does the fix remove the false-alarm class without losing real paths, and does `AG003` rule-faithful precision on a third, unseen sample improve over v2's 0.83?
2. What fraction of injected defects does the tool find, per defect type (recall by mutation)?
3. Does an injected defect cause any *other* new finding (collateral false alarms)?

## New corpus F2

- **Repositories:** `gh search repos` on the topics of F plus `spark`, language Python, **20 to 500 stars**, sorted by **most recently updated** (not by stars, so a different ordering from H and F), up to 100 per topic, not forks, not archived, name not starting "awesome", size at most 400,000 KB, and **excluding every repository cloned for H or F** (not just those sampled).
- **Files:** the same rules as H and F (15 to 1,500 lines, excluded directories, stratum by import), **at most 3 per repository**, seeded random draw (seed 3), 100 files per stratum where the pool allows. Nothing will be tuned on F2.
- **Handling:** code never committed; a manifest (repository, commit SHA, path, SHA-256) and my labels only.

## Procedure

1. Commit this protocol; implement and test v3; tag `v3-frozen`.
2. Collect F2 and commit the manifest (the tool has not been run on it).
3. Run **v2 (`v2-frozen`) and v3 once** on F2. Audit: **every `AG003` finding from either version** that does not appear in both (the instances that change), plus a seeded random 60 of the findings both versions report (so both versions' precision is estimated on the same labelled instances), and every `AG002` finding. `AG001` is unchanged, so its findings are counted but **not relabelled**.
4. Label with the rubric of the original protocol (rule-faithful, actionable), commit labels, score. Report whatever results.
5. Run the mutation study on the F2 files (below) with v2 and v3.

## Mutation study

Starting from the F2 files and using only their syntax trees to find sites, each **mutant** is one copy of a file with one change applied by replacing the source text of one expression:

| Mutation | Eligible site | Change | Target finding |
| --- | --- | --- | --- |
| **M-join** (keyless join) | `x.join(a, ...)` with a second argument or a key keyword, in a file that imports `pyspark`, receiver not a string constant or `os.path`-like name, first argument not a list or tuple | drop all arguments except the first | `AG002` at that line |
| **M-cross** (cross join) | a `join` call with a `how=` keyword whose value is a string constant, in a file that imports a dataframe library | set `how="cross"` | `AG002` at that line |
| **M-collect** (unbounded materialisation) | `X.limit(n).collect()` (or `head`, `take`, `sample`, `first`, `slice`, and `toPandas`/`to_pandas`) with the bounder immediately before the materialiser, root of the chain not a name assigned from a bounded expression | remove the bounder call | `AG001` at that line |
| **M-path** (hard-coded path) | a call to `read_csv`, `read_parquet`, `read_json`, `read_excel`, `csv`, `parquet`, `json`, `load` or `scan_*`, first argument not a constant | replace the first argument with `"/mnt/data/input.dat"` | `AG003` at that line |

Up to 100 mutants per type, drawn with a fixed seed from the eligible sites in different files first. A mutant is **found** if the target rule has a finding whose line span covers the mutated line. **Recall** = found / mutants with a Wilson 95% interval, per type and version. **Collateral** = findings in the mutant beyond the original file's findings plus the one expected, per type.

## Pre-stated expectations (written so they can be wrong)

- **AG003 on F2:** v2 rule-faithful precision 0.75 to 0.90 (the new sample has different repositories and may carry other false-alarm classes); v3 at least 0.04 higher than v2 on the instances that changed, and v3 overall at least 0.85. Actionable precision stays below 0.3 for both.
- **The fix does not lose real paths:** every instance removed by v3 is labelled not rule-faithful; I expect at most one exception.
- **Recall by mutation:** M-path 0.95 or higher; M-collect 0.90 or higher; M-cross 0.95 or higher; **M-join below M-path**, between 0.7 and 0.95, because a call stored in an alias or reached through an unusual receiver can be missed; v3 equals v2 for the three rules not touched by the fix.
- **Collateral:** at most 2% of mutants gain an extra finding.

## Limits, stated in advance

Mutation measures recall for *injected* instances of simple surface forms, not recall for defects people actually write; the sites are chosen by the same syntax the tool uses, which flatters the tool. Real recall is lower. One rater who wrote the tool. F2 is a convenience sample of less popular repositories. The v3 exclusions are chosen from the v2 audit and could over-fit its few examples; F2 is the check.

## Deviations

1. **The protocol and the v3 code were committed together** (e72a272), not the protocol first. The protocol file was written before the code, and no new file had been collected or analysed at that point, but the commit order does not prove it.
2. **Collected corpus F2 has 223 files, not about 300 (before the tool was run on it).** The Polars stratum supplied only 23 files (11 repositories) under the 3-per-repository cap in the star band; PySpark and pandas gave 100 each; 91 repositories in all. 350 repositories (those cloned for H and F) were excluded. I did not relax the cap or the band.
3. **The mutation study on F2 alone is too small for three of four types, so a pooled run was added (exploratory; logged after the F2 mutation run, before reading anything else from it).** F2 supplied 16 eligible `M-join` sites, 3 `M-cross` and 1 `M-collect` (95 `M-path`). The pre-stated recall comparison cannot be made from that, so I also ran the identical mutation procedure on the pooled files of H (300), F (288) and F2 (223); this is exploratory, uses the same seed and sampling, and the F2-only numbers remain the protocol's result. The H and F files were read during earlier audits, which does not matter for mutation (the defects are injected), but it is a different population from F2.
