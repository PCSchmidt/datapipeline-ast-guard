# Results v3: the AG003 route/parameter-name fix, and recall by mutation

Plan: [PROTOCOL_V3.md](PROTOCOL_V3.md), with three deviations logged (see the end). v2 (tag `v2-frozen`) and v3 (tag `v3-frozen`) were each run **once** on corpus F2: 223 files, 45,171 lines, 91 repositories that were not used for H or F (350 repositories excluded). Builds on [RESULTS_V2.md](RESULTS_V2.md).

> **Read this first.** One rater, who is also the tool's author. The v3 exclusions were chosen from the v2 audit; F2 is the check. F2 is a convenience sample of recently updated, less popular repositories, and findings cluster inside a few of them (one repository supplied 8 of the 62 audited findings). The mutation study is **close to a unit test of the plain forms**, not an estimate of real-world recall.

## 1. Did the fix work? (`AG003` on F2)

| | v2 | v3 |
| --- | --- | --- |
| Findings reported | 78 | 76 |
| Rule-faithful precision (labelled instances) | 54/62 = 0.871 [0.766, 0.933] | 54/60 = **0.900** [0.799, 0.953] |
| Weighted over all findings | 0.877 | 0.900 |
| Actionable precision | 9/62 = 0.145 [0.078, 0.253] | 9/60 = 0.150 [0.081, 0.261] |

- **The fix removed exactly the instances it targeted and nothing real.** v3 drops two findings, both AWS Systems Manager parameter names (`get_parameter(Name="/emr_demo/silver_bucket")`), both labelled not-a-path. No real path was lost (the pre-stated "at most one exception" held: zero).
- **The gain is small: +0.023.** I had expected at least +0.04. F2 contained far fewer instances of the targeted class than the v2 sample (2 against 9), because the class is concentrated in a few repositories, so the fix could not move the overall number much. The overall v3 figure (0.90) meets the "at least 0.85" expectation.
- **Remaining false alarms (6 of 60 audited under v3), by kind:** two regular expressions (`re.compile(r"/ICD10/([^/]+)")`), two MLflow experiment names (`mlflow.set_experiment("/demo/ai_platform_churn")`), one SSM name built by concatenation (`"/hopsworks/role/" + role + "/type/" + key`, then passed as `Name=`), and one `location.replace("s3://", "")`. **The experiment-name class is new; the concatenated name and the regex are the kinds v3 does not handle.** None was fixed; each would need its own fresh sample to test.
- **The rest of the picture is unchanged:** actionable precision stays at 0.15 (hard-coded buckets and Windows or HDFS paths in code that looks production-style; most findings are `/tmp` scratch files, placeholders, demo data and bucket names built from configuration).
- **`AG002`:** 3 findings under both versions, all false (an RDD key join, a pair-RDD join with a keyword argument, and a `str.join` on an attribute). Across the three studies (H, F and F2) `AG002` has produced no true keyless or cross DataFrame join in real code.
- **Regression checks, v3 against v2:** identical on the original 300 files of H (73 flagged files, 113 `AG001`, 51 `AG003`, 1 `AG002`) and on the challenge set (46/3/1, 21/18/1, 32/2/1, 8; the `AG002` row is the v2 import-gating effect described in RESULTS_V2).

## 2. Recall by mutation

A mutant is an F2 file with one expression replaced so that it contains a known defect; found means the target rule reports on that line. 223 files, seed 3, at most 100 mutants per type, no mutant failed to parse.

| Mutation | Eligible sites on F2 (files) | Mutants | Found, v2 | Found, v3 | Extra findings caused |
| --- | --- | --- | --- | --- | --- |
| keyless join (`AG002`, PySpark files) | 16 (9) | 16 | 16/16 = 1.00 [0.81, 1.00] | 16/16 | 0 |
| cross join via `how="cross"` (`AG002`) | 3 (3) | 3 | 3/3 [0.44, 1.00] | 3/3 | 0 |
| unbounded materialisation (`AG001`, bound removed) | 1 (1) | 1 | 1/1 [0.21, 1.00] | 1/1 | 0 |
| hard-coded path (`AG003`, argument replaced) | 95 (49) | 95 | 95/95 = 1.00 [0.96, 1.00] | 95/95 | 0 |

F2 alone is too thin for three types, so I also ran the same procedure on the pooled files of H, F and F2 (exploratory, Deviation 3): keyless join 86/86 [0.96, 1.00], cross join 87/87 [0.96, 1.00], unbounded materialisation 18/18 [0.82, 1.00], hard-coded path 100/100 [0.96, 1.00], for both versions, with no extra findings caused. In the path mutants, 4 of the 100 replaced an argument that was already an f-string path the tool flagged, so those count as found for a trivial reason.

**What this means.** The tool finds every injected defect in the plain surface forms, and injecting one never changes anything else. That is a useful sanity check (the rules do not have a hidden gap in the forms they claim), but it is not a recall estimate: the sites are chosen from the same syntax the tool reads, which makes the exercise generous. My pre-stated expectation that keyless-join recall would be "between 0.7 and 0.95" was wrong, and the reason is that I only mutated calls the tool is built to see. Defects written in indirect forms (a method stored in a variable, `getattr`, a custom wrapper) were measured on the challenge set, where the tool misses them by design.

## Against the expectations written in advance

| Expectation | Outcome |
| --- | --- |
| `AG003` v2 precision 0.75 to 0.90 | Yes (0.871) |
| v3 at least 0.04 above v2 and at least 0.85 overall | **Overall yes (0.90); the +0.04 gain no** (+0.023) |
| Every instance v3 removes is not rule-faithful, at most one exception | Yes (0 exceptions, 2 removed) |
| Actionable `AG003` below 0.3 | Yes (0.15) |
| `M-path` 0.95 or higher | Yes (1.00) |
| `M-collect` 0.90 or higher | Yes on the pooled run (18/18); F2 alone has one site |
| `M-cross` 0.95 or higher | Yes (3/3; pooled 87/87) |
| `M-join` below `M-path`, between 0.7 and 0.95 | **Wrong** (16/16 and 86/86) |
| v3 equals v2 for the untouched rules | Yes |
| Extra findings in at most 2% of mutants | Yes (0%) |

## What this does and does not show

- **Shown:** the v3 exclusions remove their target class without removing real paths; the rules find every injected plain-form defect without side effects; `AG002` and `AG001` still have no demonstrated value on real code beyond what v1 showed.
- **Not shown:** recall in the wild; that the new exclusions generalise beyond these samples (F2 held only two instances of the class); the unaddressed false-alarm kinds (experiment names, concatenated parameter names, regular expressions).
- **Not claimed:** that `AG003` is now good. It is 0.90 rule-faithful and 0.15 actionable on a new sample, which is a warning to look at, not a gate.

## Deviations and process notes

1. The protocol and the v3 code were committed together, not protocol first.
2. F2 has 223 files, not about 300: the Polars stratum supplied 23 files under the per-repository cap.
3. The pooled mutation run was added after F2 alone proved too thin; it is exploratory.
4. `AG001` is unchanged in v3 and was not relabelled on F2 (36 findings counted only).

## Limits

One rater who wrote the tool. A convenience sample; findings cluster by repository, so the intervals (which treat findings as independent) are optimistic. The mutation sites are the tool's own syntax. The v3 exclusions are tuned to classes seen in two audits and may need adjusting as new ones appear.

## Reproduce

```bash
python scripts/collect_fresh2.py                      # clones; code stays local
python scripts/evaluate.py run --corpus fresh2 --split all --rules v2-frozen --out results/fresh2_v2-frozen.json
python scripts/evaluate.py run --corpus fresh2 --split all --rules v3-frozen --out results/fresh2_v3-frozen.json
python scripts/audit_fresh2.py draw                   # then label, then:
python scripts/score_fresh2.py
python scripts/mutate.py                              # F2 only; `pooled` adds H and F
```
