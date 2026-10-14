# Protocol v4: closing the AG003 false-alarm kinds found on F2, and checking whether new ones keep appearing (written before the rule changes were coded and before any new file was collected)

Follows [PROTOCOL_V3.md](PROTOCOL_V3.md) and [RESULTS_V3.md](RESULTS_V3.md). The v3 audit on 223 unseen files left six false alarms among 60 audited `AG003` findings, in four kinds: regular expressions that start with a slash (`re.compile(r"/ICD10/([^/]+)")`), MLflow experiment names (`mlflow.set_experiment("/demo/churn")`), an SSM parameter name built by concatenation and passed as `Name=` (`"/hopsworks/role/" + role`), and a scheme used as an argument of a string method (`location.replace("s3://", "")`). Each v2 and v3 fix removed the class it targeted and the next sample showed new classes. This study fixes the four kinds and asks whether that pattern continues.

## What changes in v4 (decided now from the F2 audit; `AG001` and `AG002` unchanged)

`AG003` stops reporting a string constant when it is:

1. an argument of a call to `compile`, `match`, `search`, `fullmatch`, `sub`, `subn`, `findall`, `finditer` or `split` on a receiver named `re` or `regex`;
2. the first argument of a call to `set_experiment`, `get_experiment_by_name` or `create_experiment`;
3. anywhere inside the value of a keyword argument named `Name` or `SecretId` (v3 skipped only a bare constant, so a concatenation was missed);
4. an argument of a call to the string methods `replace`, `split`, `rsplit`, `strip`, `lstrip`, `rstrip`, `partition`, `rpartition`, `count`, `find`, `index` (v3 handled only `startswith`, `endswith`, `removeprefix` and `removesuffix`).

Each exclusion gets a regression test that also asserts a neighbouring real path is still reported. v4 is frozen and tagged `v4-frozen` before the new sample is analysed. Protocol committed before the code this time.

## Questions

1. Does the fix remove its four kinds without removing real paths, and does `AG003` rule-faithful precision improve on a fourth unseen sample (F3)?
2. Do new false-alarm kinds appear in F3 that no existing rule covers? If every sample keeps revealing new kinds, a rule list of this form does not converge.

## New corpus F3

- **Repositories:** the topics of F2, language Python, 20 to 500 stars, **newest created first** (not most recently updated, not by stars: another ordering, and newer repositories, which are more likely to contain AI-assisted code), up to 100 per topic, not forks, not archived, name not starting "awesome", size at most 400,000 KB, and **excluding every repository cloned for H, F or F2**.
- **Files:** as for F2 (15 to 1,500 lines, excluded directories, stratum by import), at most 3 per repository, seeded random draw (seed 4), up to 100 files per stratum. Nothing is tuned on F3.
- **Handling:** code never committed; manifest and labels only.

## Procedure

1. Commit this protocol; implement and test v4; tag `v4-frozen`.
2. Collect F3 and commit the manifest.
3. Run **v3 (`v3-frozen`) and v4 once** on F3. Audit: **every `AG003` finding that only one version reports**, plus a seeded random 60 of those both report, plus every `AG002` finding. `AG001` is not relabelled.
4. Label with the established rubric (rule-faithful, actionable), commit labels, score. For each remaining false alarm, name its kind.
5. Regression checks (report only): the original 300-file corpus H, the challenge set C, F and F2 with v3 and v4.

## Pre-stated expectations (written so they can be wrong)

- **The fix works on what it targets:** every instance v4 removes from F3 is not rule-faithful, at most one exception.
- **The gain is small:** v4 rule-faithful precision minus v3's is between 0 and +0.03.
- **New kinds appear:** at least two distinct false-alarm kinds in F3's remaining `AG003` findings that are not among the four above or the v2 and v3 kinds. (If none appear, I will say the list may be converging.)
- v3 rule-faithful precision on F3 between 0.75 and 0.92; actionable precision below 0.25 for both.
- On F, F2 and H, v4 changes at most 8 findings relative to v3, all of them labelled false alarms where a label exists.

## Limits, stated in advance

One rater who wrote the tool. F3 is a convenience sample of new repositories; findings cluster by repository, so the intervals are optimistic. The v4 exclusions are designed from six examples. A pre-registered prediction that the list will not converge is a prediction about this tool, not about static analysis in general.

## Deviations

(none yet)
