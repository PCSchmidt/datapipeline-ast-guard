# Results: first measured detection quality

Plan: [PROTOCOL.md](PROTOCOL.md), pushed before anything was generated, collected or scored, with three deviations logged (all before the test halves were scored). Two versions of the tool are scored: **v0**, the tool as shipped (tag `v0-as-shipped`), and **v1**, after fixes made on development data only (tag `v1-after-dev`). Both were run **once** on the held-out test halves.

> **Read this first.** Every label is mine, and I wrote the tool: one rater, no agreement statistic. The real code is a convenience sample (popular public repositories, 300 files from 83 repositories), not a random sample of data pipelines. The model-written corpus contains only 27 labelled positives, and **none for `AG002`**. Numbers are small-sample estimates with wide intervals, and "precision" is measured on the tool's findings, not on all code.

## What was measured

| Corpus | What it is | Size |
| --- | --- | --- |
| **H** | real human-written pipeline code (PySpark, Polars, pandas) from public GitHub repositories, never committed | 300 files, 91,468 lines, 83 repositories (168 files development, 132 test, split by repository) |
| **G** | scripts written by four local models (Qwen2.5-Coder 7B, Mistral 7B, Llama 3.2 3B, Gemma 4 12B) for 50 data-engineering tasks, labelled by me **before the tool was run** | 200 generations: 198 contain code (190 parse, 8 do not), 2 had no code block; 27 labelled positives (12 `AG001`, 15 `AG003`, 0 `AG002`) in 17 scripts |
| **C** | constructed challenge set, expectations written before the tool was run on it | 133 snippets (3 judged unclear) |

Two labels per instance: **rule-faithful** (the instance is what the rule's own definition describes) and **actionable** (a data engineer reviewing the change would want to look). They are different on purpose; see the protocol.

## 1. How noisy is it on real code? (H, all 300 files)

| | Files flagged [95% interval over repositories] | Findings per 1,000 lines |
| --- | --- | --- |
| v0, all files | **27.3%** [20.9, 34.4] | 2.36 [1.55, 3.45] |
| v0, PySpark | 38.0% [25.3, 53.4] | 4.51 [2.15, 7.85] |
| v0, Polars | 30.0% [21.4, 39.5] | 2.08 [1.27, 3.20] |
| v0, pandas | 14.0% [7.8, 21.6] | 0.94 [0.47, 1.59] |
| v1, all files | **25.0%** [18.8, 31.9] | 1.85 [1.23, 2.68] |

v0 produced 216 findings on these files (114 `AG001`, 15 `AG002`, 87 `AG003`); v1 produced 169 (113, 5, 51). Runtime is about 12 ms per 1,000 lines.

## 2. Are the findings right? (audited findings on H)

I read the context around every finding (all `AG002` and `AG003`, and 60 of 70 `AG001` on development, all 44 on test) and judged each. **Test half only** (not used for any fix):

| Rule | v0 rule-faithful | v1 rule-faithful | Actionable, v0 and v1 |
| --- | --- | --- | --- |
| `AG001` unbounded collect | 37/38 = **0.974** [0.865, 0.995] | 37/38 = 0.974 | 3/44 = **0.068** [0.023, 0.182] |
| `AG002` keyless join | 0/7 = **0.000** [0.000, 0.354] | 0/2 [0.000, 0.658] | 0/7 and 0/2 |
| `AG003` hard-coded path | 33/49 = 0.673 [0.534, 0.788] | 32/34 = **0.941** [0.809, 0.984] | 1/49 = 0.020 and 1/34 = 0.029 |

Pooled over both halves (development fixes were designed on the development half, so this is optimistic for v1): `AG001` 86/89 = 0.966 for v0 and 89/91 = 0.978 for v1, actionable 9/104 = 0.087 and 10/104 = 0.096; `AG002` 1/14 for v0 and 0/4 for v1; `AG003` 50/87 = 0.575 for v0 and 49/51 = 0.961 for v1, actionable 8/87 = 0.092 and 8/51 = 0.157. Findings judged unclear are excluded from the rule-faithful figures (15 for v0 `AG001`, mostly pyarrow tables).

What this means:

- **`AG001` is accurate and rarely worth a reviewer's time.** Almost every finding is a real `collect()` or `toPandas()` with no bound, but they are tutorial print statements, one-row assertions in exercises, scalar counts, and library conversion helpers whose purpose is the conversion. About **1 in 10** was worth looking at (the ones that were: a whole Spark frame pulled to the driver for an export, a possibly large SQL result, a streaming micro-batch). As a critical, merge-blocking rule it would be mostly noise on code like this.
- **`AG002` found one rule-faithful case in 15 audited findings, and it was not a mistake in the code.** That one was a cross join emulated with a constant key inside a dataframe library (and v1, which now recognises `keys=` as keys, no longer flags it). The other 14 were `thread.join()`, `pool.join()`, SQL string composition, RDD key joins, a Polars list-expression join, and joins whose keys were given by a keyword the tool did not know. Without type information those can look like keyless DataFrame joins; v1 removes most of them (5 findings remain on these files, none of them a keyless DataFrame join).
- **`AG003` was half noise as shipped, and the noise was mechanical.** v0's pattern matched path fragments inside f-strings, URL route strings and `startswith("file://")` tests; v1 fixes those and reaches 0.94 on unseen repositories. Even so, **only 1 in 34 remaining findings was actionable**: most are `s3://` buckets built from configuration, SageMaker container paths, and example code.

## 3. Does it catch what a model-written script contains? (G)

Test half (23 tasks, 92 scripts), then development (27 tasks):

| | v0 test | v1 test | v0 dev | v1 dev |
| --- | --- | --- | --- | --- |
| `AG001` precision | 4/11 = 0.364 [0.152, 0.646] | **4/4** = 1.000 [0.510, 1.000] | 8/9 = 0.889 | 8/8 |
| `AG001` recall | 4/4 [0.510, 1.000] | 4/4 | 8/8 [0.676, 1.000] | 8/8 |
| `AG003` precision and recall | 6/6 and 6/6 [0.610, 1.000] | 6/6 and 6/6 | 9/9 and 9/9 | 9/9 and 9/9 |
| `AG002` | no positives to score | | | |
| `AG000` (unparseable scripts) | 3 of 3 found, 0 false | same | 5 of 5, 0 false | same |

- **Recall was perfect on what was there, but there is little there.** 12 `AG001` and 15 `AG003` positives across 190 parseable scripts; the intervals are wide (lower bounds 0.76 and 0.80 pooled).
- **v0's test precision on `AG001` fell to 0.36 because of one situation:** two scripts (`S12`) take a 1% sample on an earlier line and then call `collect()` on a chain from it, which the tool treated as unbounded. That is the documented blind spot; v1's fix for it came from the challenge set, not from these scripts.
- **The models rarely wrote anything the tool targets.** 17 of the 190 parseable scripts had any positive. No model wrote a keyless or cross join, and most `collect()` calls were on one-row aggregates. The local models also differed in sloppiness: Qwen and Gemma produced code that always parsed; Mistral produced 6 scripts that do not (and 1 reply without code) and Llama 2 (and 1 reply without code), all of which the tool caught as `AG000`.

## 4. The challenge set (C): where the rules stop

| | v0 | v1 |
| --- | --- | --- |
| `AG001` | 43 right, 6 wrong, 1 unclear | 46, 3, 1 |
| `AG002` | 30, 9, 1 | 34, 5, 1 |
| `AG003` | 32, 2, 1 | 32, 2, 1 |
| `AG000` | 8 right | 8 |

**Seventeen of v0's 17 failures were cases I had marked "known hard" in advance, and v1 fixes seven of them** (a bound on an earlier line, `gc.collect()`, `sep.join(map(str, xs))`, and thread, thread-with-timeout and queue joins). What remains is by design of a name-based, type-free rule: a method stored in a variable, `getattr(df, "collect")()`, a custom class with its own `collect`, an explicit `on=None` or empty key list, a pandas `merge(how="cross")`, a variable-receiver `sep.join(parts)`, UNC paths, and an upper-case `S3://`. I also expected the tool to flag a path mentioned in a docstring, regular expression or log message; it does not (its pattern is anchored at the start of the string), so those three cases were handled correctly.

## 5. Robustness

Findings were **identical under all four behaviour-preserving transformations** (reformatting through `ast.unparse`, renaming every local variable, adding comments, wrapping module code in a function) for both versions, on all 300 real files (168/168 development, 132/132 test) and on all 190 parseable model-written scripts (101/101 development, 89/89 test).

## Against the expectations written in advance

| Expectation | Outcome |
| --- | --- |
| More than a third of PySpark files flagged | Yes for v0 (38%), but the interval is wide (25% to 53%); v1 36% |
| Polars flagged mostly for `collect()` | Yes (43 of 74 findings) |
| pandas flagged mostly for index `join` and a few `toPandas` | **Wrong.** No index join appeared; pandas findings were `to_pandas` calls on Arrow tables and path strings |
| Actionable precision well below rule-faithful precision for `AG001` and `AG002` | Yes, and far below (0.07 against 0.97 for `AG001`) |
| `AG003` has the highest rule-faithful precision | **Wrong** for v0 (0.58 pooled); right only after the fixes (0.96) |
| Model-written recall above 90% | Yes (12/12 and 15/15), with very few positives; `AG002` unmeasurable |
| Moderate `AG001` precision on model-written scripts | Yes for v0 (0.36 on test); v1 is clean on this sample |
| Recall near 100% on direct forms, low on indirect ones | Yes |
| Stable under reformatting, renaming and comments | Yes, perfectly |
| As shipped, too noisy to block merges on real code; improves materially after fixes | **Half right.** Yes too noisy. `AG003` and `AG002` improved materially, but `AG001`, the rule most likely to block a merge, did not become more actionable: its noise is context, not a detection bug |

## What this does and does not show

- **Shown:** the rules do what they say, deterministically, fast and stably; most of their *false alarms* on real code were mechanical and fixable; and, measured honestly, the tool flags about a quarter of real pipeline files, and only roughly one in ten of its `AG001` findings (and about one in six of v1's remaining `AG003` findings) was something a reviewer would want to look at.
- **Not shown:** recall on real code (it would need every file labelled); any effect on engineers; behaviour on SQL, notebooks (`.ipynb`) or code in other languages; whether the findings are worth their cost compared with a type-aware linter.
- **Not claimed:** that v1 is "good". It is better on the defects found here. Its `AG001` severity (critical) is hard to justify on this evidence, and `AG002` has not been shown to find anything on real code.

## Deviations and process notes

1. The first model-written corpus ignored the framework because the prompts did not name it; it was discarded unscored and regenerated with the framework named (Deviation 1).
2. Three bookkeeping errors in the challenge set and scorer were corrected after the first run on it, without changing the tool (Deviation 2).
3. The development log of v0 to v1 is in the protocol (Deviation 3). Fixes used only development data and the challenge set; the earlier-line-bound fix was designed from the challenge set and then replicated, by accident of the split, on the test half of G (seven false positives removed).
4. I saw the code of the test scripts and findings while labelling them, after v1 was frozen; no change was made after that.

## Limits

One rater who is also the author; no inter-rater agreement. A convenience sample of popular repositories sorted by stars, with at most five files per repository. The audit covers the tool's findings, not all code. Local models at one temperature and one sample each. 27 positives. The challenge set was written by the tool's author and can expose defects but not certify coverage. The repository-level bootstrap uses 83 repositories.

## Reproduce

```bash
pip install -e ".[dev]"
python scripts/collect_human.py                          # clones the repositories; code stays local
python scripts/generate_corpus.py                        # needs a local Ollama server with the four models
python scripts/evaluate.py challenge --rules v0-as-shipped
python scripts/evaluate.py challenge --rules v1-after-dev
python scripts/evaluate_extra.py score-generated --split test --rules v1-after-dev
python scripts/evaluate_extra.py audit --split test --rules v1-after-dev      # then score-audit with the committed labels
python scripts/summarise_human.py && python scripts/pool_results.py
```

Labels are in `corpus/labels_generated.json` and `corpus/labels_audit.json`; the human-code manifest (repository, commit SHA, path, file hash) is in `corpus/manifest_human.jsonl`; the code itself is never committed. Model-written scripts are committed for the Apache-2.0 models only (Qwen, Mistral).
