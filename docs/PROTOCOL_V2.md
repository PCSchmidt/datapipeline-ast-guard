# Protocol v2: severity and AG002 scope changes, re-measured on unseen repositories (written before the changes were coded, before any new file was collected and before the tool was run on it)

Follows [PROTOCOL.md](PROTOCOL.md) and [RESULTS.md](RESULTS.md). That study found: v1 flags 25% of real files; `AG001` (critical) is accurate but only about 1 in 10 findings is worth a reviewer's time; `AG002` has not been shown to find a real keyless DataFrame join; `AG003` reached 0.94 rule-faithful precision, measured on repositories whose errors I had just read. This protocol decides what to change and how to test it **on code I have never read**.

## What changes in v2 (decided now, from the v1 evidence and from library semantics; no detection logic for `AG001` or `AG003` changes)

1. **`AG001` becomes a warning.** The pattern is right; the evidence says it is not merge-blocking material. Severity is policy, not detection, so no re-tuning of the rule itself.
2. **`AG002` is split by form, within the one rule ID.**
   - *Explicit cross join* (`crossJoin(...)`, `how="cross"`): stays **critical**, and is reported only if the file imports a dataframe library (`pyspark`, `pandas`, `polars`, `pyarrow`, `duckdb` or `ibis`). Cross joins are unambiguous and rare.
   - *Keyless `.join(other)`*: becomes a **warning** and is reported only if the file imports `pyspark`. Reason (library semantics, not data): in PySpark a join with no condition is a Cartesian product; in pandas `df.join(other)` joins on the index by design, and Polars requires `on` or `how="cross"`, so a keyless call there is not the hazard the rule describes.
3. **CLI:** `--fail-on {critical,warning,never}` (default `critical`, so the default exit code is unchanged in meaning but, with `AG001` demoted, fires far less). Message texts follow severity.

Each change gets a regression test. v2 is frozen and tagged `v2-frozen` **before** the new sample is analysed.

## Questions

1. Does v1's `AG003` precision (0.94 on the previous test half) hold on repositories nobody read before?
2. How much of the flagged-file noise is removed by v2's changes, and how many files would **fail the default gate** (exit 1) under v1 and under v2?
3. Does `AG002` (either form) find any rule-faithful case on the new sample?
4. Does `AG001`'s actionable precision stay near 0.1 (so that demoting it was right), or was the previous estimate unlucky?

## New corpus F (fresh code)

- **Repositories:** `gh search repos` on the topics `pyspark`, `polars`, `etl`, `data-pipeline`, `data-engineering`, `airflow` and `spark`, language Python, **20 to 500 stars** (previously the top 40 per topic by stars, so this is a different, less famous population), up to 60 per topic by stars within that band, not forks, not archived, name not starting "awesome", size at most 400,000 KB, and **not in `corpus/manifest_human.jsonl`**.
- **Files:** the same rules as H (15 to 1,500 lines, excluded directories, stratum by import), **at most 3 per repository** (previously 5, to spread over more repositories), seeded random draw (seed 1), **100 files per stratum, 300 in all**. No development/test split: nothing will be tuned on F.
- **Handling:** code never committed; a manifest (repository, commit SHA, path, file SHA-256) and my labels only.
- **Confound, stated in advance:** F differs from H in star band and per-repository cap, so a different flagged-file rate cannot be attributed to the tool change alone. Question 2 is therefore answered by running **v1 and v2 on the same F files**, not by comparing F with H.

## Procedure

1. Commit this protocol, then implement and test the v2 changes, then tag `v2-frozen`.
2. Collect F and commit the manifest (the tool has not been run on it).
3. Run **v1 (`v1-after-dev`) and v2 (`v2-frozen`) once** on F. Draw the audit sample: **every finding for `AG002`, and a seeded random 60 for each of `AG001` and `AG003`**, taken from the union of v1 and v2 findings so that both versions are judged on the same instances.
4. Label with the same rubric as the original study (rule-faithful; actionable), commit labels, then score. Report whatever results, including a drop in `AG003` precision.
5. Re-run the challenge set C and the original H split as **regression checks** only; report them, change nothing.

## Metrics

Per rule rule-faithful and actionable precision with Wilson 95% intervals for each version; flagged-file rate and findings per 1,000 lines with repository-level bootstrap intervals; share of files that would fail the default gate under v1 and v2; challenge-set outcomes for v2.

## Pre-stated expectations

- `AG003` rule-faithful precision on F for v1 between 0.80 and 0.95; I expect it to be **lower than 0.94**, because the fixes were fitted to the repositories used before. Actionable stays below 0.2.
- `AG001` rule-faithful above 0.9; actionable between 0.03 and 0.2.
- `AG002`: fewer than 5 findings under v2 on F, and **zero or one** rule-faithful. Under v1 several false alarms.
- Files failing the default gate: v1 roughly 10% to 20% of files; v2 below 3%.
- The challenge set: v2 will lose the cases where `AG002` was expected on a keyless pandas/Polars `join(other)` that I had written as positives, and I will list them rather than rescore them.

## Limits

Same single rater who wrote the tool. 300 files from a convenience sample of less popular repositories; recall on real code is not measured. The demotions are policy decisions made on the previous evidence; this study checks their consequences, not whether a team should block on them.

## Deviations

1. **Collected corpus F has 288 files, not 300 (2026-10-12, before the tool was run on it).** The Polars stratum could supply only 88 files under the 3-per-repository cap (38 repositories had Polars files in the star band); PySpark and pandas gave 100 each. 116 repositories in all. I did not relax the cap or widen the band to reach 300.
