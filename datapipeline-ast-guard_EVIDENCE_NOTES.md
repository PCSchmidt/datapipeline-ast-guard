# datapipeline-ast-guard: Evidence Notes

Companion to `datapipeline-ast-guard.md`. Labels: Confirmed, Ran it, Per the docs, My reading, Ask the author, Author says. Run in a scratch copy made with `git archive HEAD` (old explainer file removed, never read); the clone was not written to.

## E1 Fact sheet
- Name datapipeline-ast-guard, MIT licence, version 0.5.0 (`pyproject.toml`). Confirmed.
- Kind: command-line static-analysis tool (`agent-lint`) plus evaluation studies. Python >=3.11, one runtime dependency (`click>=8.1`). Confirmed.
- Size: `rules.py` 368 lines; 28 tests; 14 study scripts; 35 commits, 2026-10-09 to 2026-10-19 (last code commit 2026-10-14). Confirmed.
- Tags: v0-as-shipped, v1-after-dev, v2-frozen, v3-frozen, v4-frozen, v0.4.0, v0.5.0. Confirmed.
- Deployed: no. Not on PyPI (README). No users shown. Confirmed / Per the docs.
- Related: rag-audit, entity-resolution-gate, meridian family (same "gate before trust" idea). My reading.

## E2 Reading and running log
Read: README, all docs (PROTOCOL, RESULTS, PROTOCOL/RESULTS V2 to V4 in part), `rules.py`, `cli.py`, `report.py`, tests, CI, Dockerfile, pyproject, `generate_corpus.py`, `tasks.json` head, commit log. Not read: any earlier explainer (including the one committed in the repo and its history), labels files in detail, the other study scripts line by line. Not run: Docker build, study scripts (need cloned corpora and Ollama), `.env` (none exists).
Commands (scratch copy, Python 3.14.6, fresh venv, `pip install -e ".[dev]"`):
- `pytest -q -p no:cacheprovider` -> 28 passed in about 2 s. Ran it.
- `mypy src tests` -> Success, no issues in 5 source files. Ran it.
- `ruff check src tests` -> all checks passed; `ruff check src tests scripts` -> 1 error (F841 unused variable `a_no`, `scripts/pool_results.py:46`). `ruff format --check src tests` -> 5 files formatted. Ran it.
- Coverage (`coverage run --include='src/*' -m pytest`): total 94% (rules.py 92%, 17 of 225 statements missed). Ran it.
- `agent-lint examples/agent_written_pipeline.py` -> 5 findings (AG003 l7, AG003 l8, AG002 warning l10, AG002 critical l11, AG001 l13), exit 1. Matches README. Ran it.
- Installed versions: click 8.5.0, hypothesis 6.170.12, pytest 9.1.1, mypy 2.4.0, ruff 0.17.3. Dependencies are not pinned. Ran it.
- Final `git status --short` in the clone: empty (no tracked changes). Confirmed.

## E3 Claims check (levels: L1 doc matches committed result file; L2 re-run; L3 recomputed)
| ID | Claim | Level | Verdict |
| --- | --- | --- | --- |
| CL-01 | Example output, five findings, exit 1 | L2 | supported |
| CL-02 | 28 tests pass (quickstart) | L2 | supported |
| CL-03 | "Tests: 10" (At a glance table) | L2 | contradicted (stale) |
| CL-04 | "benchmark corpus is not built yet, so no precision or recall numbers" (What's real) | L1 | contradicted by the same README's Results section |
| CL-05 | mypy strict, ruff clean | L2 | partly (ruff clean on src and tests; 1 finding in scripts) |
| CL-06 | Findings identical under four rewrites | L1 | supported per result files (`results/metamorphic_*`); not re-run |
| CL-07 | Default gate fails 20.8% of files under v1, 0 real under v2 | L1 | supported against RESULTS_V2 |
| CL-08 | AG001 3/44 actionable on test half | L1 | supported against RESULTS.md |
| CL-09 | AG003 precision 0.94, 0.83, 0.87-0.90, 1.00 | L1 | supported against RESULTS docs; README says 0.87 to 0.90 for v3 |
| CL-10 | Mutation recall 100% plain forms | L1 | supported (RESULTS_V3); caveat in docs |
| CL-11 | About 12 ms per 1,000 lines | Per the docs | not re-measured |
| CL-12 | Docker image builds and passes tests offline | Per the docs | not run |
| CL-13 | "Pre-registered" protocols | L1 | partly: commit order checked (E8); push times not visible; v3 protocol and code in one commit (disclosed in RESULTS_V3) |
| CL-14 | RESULTS.md calls AG001 "critical" in its not-claimed note | L1 | stale wording (v1-era); README and code say warning |

## E4 Rule attacks (scratch copy, `probe.py`, direct calls to `analyze_source` and the CLI)
Empty file: none. `def f(:`, Python 2 print, null byte: AG000 critical, exit 1. `df.collect()` with pyspark import: AG001. `df.limit(5).collect()`: none. `df.sample(0.01).collect()`: none (sample is in the bound set). `getattr(df,'collect')()` and `f = df.collect; f()`: none. Cap in another function (`a().collect()`): flagged. `s = df.limit(5); s = spark.read.parquet(p); s.collect()`: flagged (rebinding drops the cap). `join(b, on=None)` and `join(b, [])`: none. `a.crossJoin(b)` with no import: none. pandas `merge(how='cross')`: none. `join(how='cross')` with polars import: AG002 critical. pyspark `a.join(b)`: AG002 warning. pandas `a.join(b)`: none. `sep.join(parts)` with pyspark import: AG002 warning. `"/data/in"` default in `os.environ.get`: AG003. `"./data/x.csv"`, `"S3://b/k"`: none. Module docstring starting `/data/x.csv`: AG003. `f"{b}/data/x"`: none. Muting comment on a later line of a multi-line chain: not muted (finding reported at the first line of the expression). Muting comment for another rule: not muted. 500 nested parentheses: AG000 (Python's parser rejects). 20,000-term `a+a+...` and a 5,000-method chain: RecursionError traceback (CLI exit 1). File containing a non-UTF-8 byte: UnicodeDecodeError traceback (CLI exit 1). `--fail-on never` with unparseable file: exit 0; default: exit 1. Nonexistent path: click usage error. All Ran it. A probe of a Windows path with `\x` in the string was my own escape error (AG000 came from Python's parser), not a tool defect.

## E5 Code map
- `src/datapipeline_ast_guard/rules.py`: `analyze_source`, `_Visitor` (AG001 in `visit_Call`, AG002 in `_check_join`/`_join_form`, AG003 in `visit_Constant` plus exclusions in `visit_Call`, `visit_keyword`, `visit_JoinedStr`, `visit_BinOp`), `_suppressed`, `RULES`.
- `cli.py`: click command `agent-lint`; `--format json|sarif`, `--fail-on critical|warning|never`; reads `*.py` recursively.
- `report.py`: JSON and SARIF 2.1.0.
- `tests/test_rules.py`: 28 tests (one Hypothesis property test, `test_never_raises_on_arbitrary_text`, text up to 300 chars).
- `scripts/`: collectors for each sample, `generate_corpus.py`, `evaluate.py`, `evaluate_extra.py`, `mutate.py`, scorers and summaries. `corpus/`: manifests, labels, tasks, challenge cases, committed model scripts (Qwen and Mistral only). `results/`: 43 JSON result files. `docs/`: four protocols, four results documents.
- Entry points: `agent-lint` and `datapipeline-ast-guard` (same function).

## E6 Model call sites
Only in `scripts/generate_corpus.py`, `chat()`: local Ollama at `localhost:11434/api/chat`, `stream=False`, options temperature 0.7, seed per (task, model) from SHA-256, `num_predict` 1800; `think=False` for Gemma. Models: `qwen2.5-coder:7b-instruct-q4_K_M`, `mistral:7b-instruct-v0.3-q4_K_M`, `llama3.2:3b-instruct-q8_0`, `gemma4:12b`. System prompt: "You are a data engineer. Reply with one complete Python script in a single code block." User prompt: task text + " Use PySpark." / " Use Polars." / " Use pandas.". Manifest (200 rows): per-model ok counts qwen 50, mistral 49, llama 49, gemma 50; framework split 80/60/60; summed seconds qwen 745.7, mistral 586.7, llama 397.6, gemma 1139.5 (about 2,870 s, 48 min). Confirmed. Cost: no paid call; electricity and hardware not recorded (Ask the author for the machine, not documented in the repo). No model is called by the tool.
Licences: Qwen and Mistral Apache 2.0 per PROTOCOL.md; Llama and Gemma redistribution terms "not checked" per PROTOCOL.md. Per the docs.

## E7 Tests and CI
28 tests, 0 skipped, 94% statement coverage of `src`. CI (`.github/workflows/ci.yml`): on push and pull request, ubuntu, Python 3.12, `pip install -e ".[dev]"`, `mypy src tests`, `pytest -q`. No ruff, no evaluation, no branch protection visible (not checked on GitHub). Dependabot monthly (Actions and pip). Spot checks: `test_cli_exit_codes` asserts real exit codes for ok, warning, bad, `--fail-on warning`, `--fail-on never` (real behaviour). `test_inline_suppression_is_rule_specific` asserts ignore[AG001] silences AG001 and ignore[AG002] does not (real). `test_never_raises_on_arbitrary_text` asserts only that no exception and line >= 1, on text up to 300 chars (weak: does not cover deep nesting or encoding; the CLI file-read step is not under test). The ids-based tests compare rule IDs only, not line or column except in the SARIF test.

## E8 Plan-versus-results and history
Commit times (local, -04:00): PROTOCOL 2a99c1c 2026-10-12 09:42; corpora and harness b67a18f 10:08; generation complete 47a0ebf 10:29; regeneration 585b381 10:29 and b97e426 11:18; blind labels 11:18 to 11:21 (several progress commits seconds apart, final 331353c 11:21); v0 on challenge set 6cf5cf7 11:23; audit labels fa1988e 11:25; v1 fb11c4c 11:29; results bc50265 11:33. V2: protocol 1158593 14:44:58, code 16365d2 14:46:04 (about one minute apart), F manifest 14:53, results 15:00. V3: protocol and rule changes in one commit e72a272 06:52 on 10-13 (disclosed). V4: protocol db0eb13 20:53:05, code ab5f5a4 20:53:47, F3 manifest a50bc1c 21:04, results ec1d927 21:14. GitHub push times not available offline; commit times are the only order evidence. My reading: the labelling of 200 scripts in the window 10:29 to 11:21 and the one-minute gaps between protocol and code commits suggest agent-driven work; the docs say labels are by one rater (the author). Ask the author.
Credits: 34 commits credit Claude Sonnet 5.5, 1 credits Claude Opus 5.5 (the commit adding an earlier explainer). All 35 under the name Chris Schmidt. No agent instruction files in the tree. Confirmed.

## E9 Gates and approvals
None (no gate engine in this repo).

## E10 Environment
Declared: click>=8.1; dev: pytest>=8, hypothesis>=6.100, mypy>=1.10, ruff>=0.5; no lockfile. Fresh install on Python 3.14.6 gave versions in E2; 28 tests pass. README says Python 3.11+; CI uses 3.12; the study results record tool tags, not package versions. Parser behaviour can depend on the Python version (My reading; not tested).

## E11 Security and privacy
Pattern scan of current tracked files (sk-, ghp_, AKIA, api_key assignments), excluding generated scripts: no hits. No `.env` present. No network or credentials in the tool; the generator talks only to localhost. Analysed code from public repositories is never committed (manifests and labels only). Generated scripts for Llama and Gemma are git-ignored. History scan not run beyond the current tree and commit messages (My reading: low risk).

## E12 Shortcomings register
| ID | Shortcoming | Severity | Disclosed | Options | Recommendation |
| --- | --- | --- | --- | --- | --- |
| S1 | CLI crashes on a non-UTF-8 file (UnicodeDecodeError) and on very deep nesting (RecursionError); no finding is produced | Medium | No | A: catch both in the file loop and emit a critical finding for the file (low cost; changes behaviour only for crashing files). B: leave and document | A; small effort, medium payoff; verify with the two probes in E4 |
| S2 | Muting comment must be on the line where the expression starts; a comment on a later line of a multi-line chain does not mute | Low-Medium | Partly (README says "on the line") | A: match the comment anywhere in the call's line span. B: document | A; small |
| S3 | `sample` counts as a cap in AG001 although it bounds a fraction, not a count | Low | Partly (listed in the bound set) | A: remove `sample`. B: keep and document | Needs a measurement first (affects precision); medium |
| S4 | Low actionable precision (about 1 in 15 to 1 in 6 for AG001; AG003 0.03 to 0.23); AG002 never shown to find a real keyless join | Medium | Yes | A: keep as warnings (done). B: add type information. C: retire AG002 | A now; B is a different project |
| S5 | One rater who also wrote the rules; clustered, convenience samples; recall on real code unmeasured | Medium | Yes | A: second rater on a subsample. B: document | A; medium |
| S6 | README stale: "Tests: 10", "benchmark not built" sentence | Low | n/a | fix text | small |
| S7 | CI runs no style check and no evaluation; versions unpinned | Low | No | add ruff to CI; pin or lock | small |
| S8 | Ordinary `pandas.merge(how="cross")` and `on=None` joins missed; upper-case `S3://` and relative paths missed | Low | Partly | document or extend | leave |
| S9 | `gemma4:12b` and the other model tags: availability changes by provider could break regeneration | Low | No | record model digests | small |
Re-run evidence for S1: E4 (crash on 20,000-term expression and latin-1 file). Ran it.

## E13 Math and method detail
Wilson 95% interval for a proportion (k of n): centre (p + z^2/2n) / (1 + z^2/n), half-width z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n), z = 1.96; implemented in `scripts/evaluate.py` `wilson`. Example 3/44: p = 0.068, interval about [0.023, 0.182] (matches RESULTS.md). Repository-level bootstrap for flagged-file rates (resampling repositories). Dev/test split by repository: first byte of SHA-256 of the full name is even for development; by task for generated scripts. Mutation: seeded (seed 3 for F2), up to 100 mutants per type. Complexity: one tree walk per file, linear in tree size (plus ancestor-chain walks per call); about 12 ms per 1,000 lines per the docs.

## E14 Discrepancies
README "Tests: 10" vs 28 (CL-03); README "no precision or recall numbers" vs Results (CL-04); RESULTS.md "Its AG001 severity (critical)" vs code and README (warning) (CL-14); README status line "Three rules ... complete" vs "Four rule IDs" (AG000 counted separately; wording only); README AG003 v3 "0.87 to 0.90" (v2 0.871 on F2, v3 0.900) consistent.

## E15 Production readiness
Placement: Works locally (some Deployable features: SARIF, container recipe, CI, Dependabot). Traits: clean-start run Yes (quickstart, versions unpinned); checks block bad change Partly (tests and types, no quality gate); quality measured against baseline Partly (no rival tool); safe failure Partly (reads only; crash cases S1); human review Not applicable/No; versioned prompts Partly (tasks and prompts committed; tool has none); logs No; secrets Yes (none needed). Gaps: package release, reusable Action, pinned versions, quality check in CI, crash handling, runbook, usage trial.

## E16 Review dispositions
Self-check against the questionnaire P4.5 done before saving; independent review passes not run in this session.

## E17 Completeness and backlog
Built and tested: AG000 to AG003, JSON and SARIF, `--fail-on`, muting. Not built (README "Known gaps"): SQL rules, unpartitioned-shuffle, missing-broadcast, null-unsafe-key and schema-assertion checks, property-based schema checks of generated code, packaged Action; PyPI release. No stubs, TODO markers or skipped tests found.
Backlog: Fix: S1, S2, S6, S7. Finish: PyPI release, Action. Improve: S5 second rater, S3 measurement. Add: SQL rules (large). Milestone 1: S1+S2+S6+S7 with exit test "every E4 probe yields a finding or message; README numbers match test run".

## Diagram sources
Images were drawn with matplotlib; the script is a scratch file (not kept in the repository). Chart values: AG001 (0.974, 0.068 test half, sample 1; 0.933, 0.167 sample 2), AG003 (0.941, 0.029; 0.827, 0.231; 0.900, 0.150; 1.000, 0.220), from RESULTS.md, RESULTS_V2.md, RESULTS_V3.md, RESULTS_V4.md.

## E18 Revision log (v1 draft to v2, reader-check fixes, 2026-10-27)
Prior version kept as `datapipeline-ast-guard.v1draft.md` (7,372 words); revised guide about 5,550 words by `wc -w`. All ten reader-check fixes applied.
1. Language-model settings (temperature, tokens, quantisation, licences, Ollama, system message) cut to a short paragraph; detail remains in the repo protocol.
2. AG001 to AG003 introduced once in plain words (big collect, risky join, fixed path) in the opening, plain names used after.
3. Critical vs warning, gate, merge, exit code, cluster, chain defined at first use and in the glossary; tokens, temperature, mypy dropped.
4. Three-checks chapter split into one short block per check with one toy example and one weakness.
5. Results prose trimmed; the chart carries the per-sample figures.
6. Probe table replaced by three sentences on the gaps that matter.
7. Terms reduced to "right by the rule" and "worth a reviewer's time".
8. Parts image regenerated: double negative replaced by "With --fail-on never, nothing can stop it." Also drops the AG0xx codes for plain names in box 3.
9. Roadmap chapter cut to three lines; rag-audit and the defense-sector aside removed.
10. Recruiter Q&A turned into bullets; table cut to four rows; length cut by about a quarter.
Determinism paragraph shortened.
Path-check figure reconciliation (from `docs/RESULTS.md`, `RESULTS_V2.md`, `RESULTS_V3.md`, `RESULTS_V4.md` in the repo; Confirmed): AG003 rule-faithful as shipped (v0) 0.673 (33/49) on the sample-1 unseen test half, 0.575 pooled over both halves (50/87); fixed (v1) 0.941 (32/34) on the unseen test half, 0.961 pooled. Later rounds: v2 0.827, v3 0.900, v4 1.00. The old text mixed the pooled 0.58 with the chart's 0.94. The chart bars are the fixed version of each round, not as-shipped; the chart footnote and the prose now say so, and the as-shipped test-half figure is stated as 0.67 with the pooled 0.58.
Images regenerated (matplotlib, scratch script, not kept): `datapipeline-ast-guard-parts.png`, `datapipeline-ast-guard-results.png`; both checked, no clipped text. Chart values unchanged.
