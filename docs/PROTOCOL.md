# Protocol: first measured detection quality for datapipeline-ast-guard (written before any script was generated, collected or scored)

Committed before the first measurement, so none of the choices below can have been made after seeing results. Anything changed later is listed under [Deviations](#deviations). The rules under test are in [src/datapipeline_ast_guard/rules.py](../src/datapipeline_ast_guard/rules.py) and the planned measurement is the one sketched in [RESULTS.md](RESULTS.md).

## Why

The tool has unit tests and a worked example but **no measured false-positive rate and no measured recall**. Its README says so. This study produces the first numbers on three kinds of code: real human-written pipelines, scripts written by local language models (the use case the tool is for), and a constructed challenge set.

## Questions

1. **How noisy is it on real code?** What share of real PySpark, Polars and pandas files does it flag, and what share of its findings are right?
2. **How well does it catch what a model-written script contains?** Per-rule precision and recall on model-written scripts that I label by reading them, before I see the tool's output.
3. **How robust are the rules?** Does it find the pattern when it is written in different surface forms, and do its findings stay the same when the code is reformatted, renamed or commented without changing behaviour?

## What I knew before writing this (stated so it can be discounted)

I read the rule implementation and wrote it. I know of three limitations in advance: it is name-based (it cannot tell a DataFrame from another object with a `collect` or `join` method); bounds are chain-local (`small = df.limit(5)` then `small.collect()` is flagged); and `sep.join(parts)` looks like a DataFrame join. I also expect, without having measured it, that Polars `LazyFrame.collect()` (the normal way to run a lazy query) and the index join `pandas_df.join(other)` will be flagged. These expectations are written down below so they can be wrong. I have not run the tool on any real corpus.

## Corpora

### H: real human-written code (false-positive profile)

- **Repositories:** public GitHub repositories found with `gh search repos` on the topics `pyspark`, `polars`, `etl`, `data-pipeline`, `data-engineering` and `airflow`, language Python, sorted by stars, not forks, not archived, up to 40 per topic; repositories whose name starts with "awesome" are dropped. Each is shallow-cloned and its commit SHA recorded. The list, dates and counts go in the results.
- **Files:** `.py` files of 15 to 1,500 lines, not in `test`/`tests`, `venv`, `site-packages`, `node_modules`, `migrations` or `vendor` directories, not named `test_*` or `__init__.py`. A file is in the **pyspark** stratum if it imports `pyspark`, in the **polars** stratum if it imports `polars`, in the **pandas** stratum if it imports `pandas` and neither of the others.
- **Sample:** per stratum, a seeded random draw (seed 0) of **100 files**, at most **5 per repository**. Development and test are split by repository: a repository is development if the first byte of `sha256(full_name)` is even.
- **Handling:** the code is read for analysis only and **never committed**. The repository contains only a manifest (repository, commit SHA, path, SHA-256 of the file) and my labels, never the code.

### G: model-written scripts (the tool's use case)

- **Tasks:** 50 realistic data-engineering tasks, written by me before generation and committed in [corpus/tasks.json](../corpus/tasks.json): 20 PySpark, 15 Polars, 15 pandas. They are phrased as ordinary requests and do not mention any pattern the tool checks.
- **Models and settings:** four local models served by Ollama, each given every task once: `qwen2.5-coder:7b-instruct-q4_K_M`, `mistral:7b-instruct-v0.3-q4_K_M`, `llama3.2:3b-instruct-q8_0` and `gemma4:12b` (thinking off). Temperature 0.7, a fixed seed per (task, model), at most 1,800 new tokens, one system message ("You are a data engineer. Reply with one complete Python script in a single code block.") and the task as the user message. The first fenced code block is the script; a reply with no code block counts as a failed generation.
- **Size:** 50 tasks x 4 models = **200 generations**.
- **Split:** by task, a task is development if the first byte of `sha256(task_id)` is even, so all four models' answers to a task are in the same half.
- **Licences:** the Qwen and Mistral models are Apache 2.0; the Llama 3.2 and Gemma terms allow the use of outputs but I have not checked redistribution, so only the **Qwen and Mistral scripts are committed**; for the other two models the repository holds only a manifest (task, model, SHA-256) and my labels.

### C: constructed challenge set (surface-form coverage)

About 150 short snippets that I write **before running the tool on them**, each with the findings it should and should not produce, grouped by rule and by surface form (aliased imports, multi-line chains, intermediate variables, keyword and positional arguments, f-strings, `Path` objects, `os.environ` defaults, non-DataFrame look-alikes such as `",".join`, `thread.join()`, `os.path.join`, `lazy.collect()` on Polars, a bounded frame on an earlier line, and so on). It is a **development** set only: it is used to find and fix defects, so it is not a held-out measure. Known-hard cases are marked as such in advance.

## Ground truth: the labelling rubric

Two labels per instance, because "matches the rule as written" and "worth a reviewer's attention" are different.

- **Rule-faithful** (the instance is what the rule's own definition describes):
  - **AG001:** a call to `collect`, `toPandas` or `to_pandas` on a dataset-like receiver with no row bound (`limit`, `head`, `take`, `first`, `sample`, `fetch`) in the same call chain **or** on an earlier statement that bounds the same frame. A Polars `LazyFrame.collect()` is rule-faithful. A `.collect()` on a non-dataset object (for example a custom class) is not.
  - **AG002:** a `crossJoin`, or a `join` on a DataFrame-like receiver with `how="cross"` or with no equality key given. `str.join`, `os.path.join`, thread and process `join` are not. A pandas `df.join(other)` (an index join) is rule-faithful (no key is given).
  - **AG003:** a string literal that is an absolute file-system path or a listed URI scheme (`s3`, `s3a`, `gs`, `abfs`, `abfss`, `hdfs`, `dbfs`, `file`, or a Windows drive path) **used as a path or URI in code**. A path inside a docstring, a regular expression, a log message or an example comment is not.
- **Actionable** (a data engineer reviewing the change would want to look): rule-faithful **and** plausibly risky in context. Examples of rule-faithful but not actionable: a Polars lazy `collect()` that produces the pipeline's final result; a `toPandas()` on a frame that an earlier line clearly reduced to a few rows by aggregation; a pandas index join; a hard-coded path in a clearly marked example or `__main__` demo.

Labels are made by me (one rater) by reading the code with the tool's output hidden, and are therefore a single-rater, same-author judgement. Where I cannot decide I record "unclear" and report those counts separately.

## Procedure and development/test discipline

1. Generate G, collect H, write C and **commit this protocol, the task file and the manifests before running the tool**.
2. Label every G script (development and test) **blind to the tool's output**, and commit the labels. Label a random audit sample of the tool's findings on H (up to 60 per rule per half).
3. **Development phase:** run the tool as shipped ("v0") on the development halves and C. Study errors, fix defects in the rules with a regression test for each, and keep a log. Only development data and C may inform a change.
4. **Freeze** the tool ("v1") and commit.
5. **Test phase:** run **both v0 and v1 once** on the test halves of G and H and report both. No change is made after seeing test results.

## Metrics

- **Per rule, rule-faithful and actionable precision** of the findings, on the audited H samples and on G, with Wilson 95% intervals.
- **Per rule recall** on G, against my blind labels, with Wilson 95% intervals; and recall on C by surface form.
- **Flagged-file rate** and **findings per 1,000 lines** on H, per stratum, with bootstrap intervals that resample repositories.
- **Metamorphic stability:** on H and G files, apply behaviour-preserving transformations (round-trip through `ast.unparse` with comments dropped; rename all local variables; add a module docstring and comments; wrap the body in a function where it is at module level) and report the share of files whose findings (rule and count) are unchanged. Differences are listed, not hidden.
- **Parse failures:** the share of model-written scripts that do not parse (AG000), by model.
- **Runtime** per 1,000 lines.

## Pre-stated expectations, written down so they can be wrong

- **H:** a high flagged-file rate in the pyspark stratum (more than a third of files), dominated by AG003 and AG001; the polars stratum flagged mostly for `collect()`; pandas flagged mostly for index `join` and a few `toPandas` calls. I expect **actionable precision well below rule-faithful precision** for AG001 and AG002, and expect AG003 to have the highest rule-faithful precision but many non-actionable hits (examples, `__main__`).
- **G:** high recall (above 90%) for all three rules at the pattern level, because the rules are simple name patterns, but moderate precision for AG001 (many bounded frames defined on an earlier line) and for AG002.
- **C:** recall near 100% on direct forms and low on aliased or indirect forms (a method stored in a variable, `getattr`), which the tool cannot see.
- **Metamorphic:** stable under reformatting, comments and variable renaming; unstable only for forms that depend on text rather than structure.
- **Overall:** as shipped, the tool is too noisy to block merges on real code without suppressions, but its precision improves materially after fixes found in development.

## Limits, stated in advance

One rater who is also the tool's author labels everything; there is no inter-rater agreement. Repositories are a convenience sample of popular public projects (sorted by stars), not a random sample of data pipelines, so flagged-file rates describe those projects. Model-written scripts come from four small local models at one temperature and one sample each. The audited sample of findings on H is not all findings. The challenge set is small and written by the tool's author, so it can only expose defects, not certify coverage. Recall on real human-written code is not measured (it would require labelling every file). Nothing here measures whether the findings change engineers' behaviour.

## Deviations

1. **The generation prompts now name the framework; the first 200 generations are superseded (2026-10-12, before any labelling and before the tool was run on the corpus).** The tasks in `corpus/tasks.json` were written without naming a framework, so when I read the first scripts I saw that most models answered in plain pandas even for tasks I had classed as PySpark, which would leave the tool's patterns (`collect`, keyless Spark joins) almost absent and recall measured on very few positives. The corpus was regenerated with the sentence "Use PySpark." / "Use Polars." / "Use pandas." appended to each task according to its `framework` field, everything else unchanged (models, temperature, seeds, system message). The first batch is kept in `corpus/superseded_v1/` (Qwen and Mistral scripts; manifest only for the others). No label had been written and the tool had not been run on any generated script. The protocol sentence "they do not mention any pattern the tool checks" still holds; they now name the library.
2. **Three bookkeeping errors in the challenge set and its scorer were corrected after running the as-shipped tool on it (no tool change).** (a) In two multi-line chains (`A1-05`, `A2-07`) I had put the expectation marker on the `out = (` line, but the tool reports a finding at the line where the call expression begins, one line later; the marker was moved. (b) Expectations were stored as a set, so a line that should produce two findings (`A3-17`) counted as one expected and one false positive; they now keep their multiplicity. (c) The unparseable snippets (`A0-01` to `A0-04`, `A0-08`) had no expectation, so a correct `AG000` was scored as a false positive; the scorer now expects exactly one `AG000` and nothing else for them. None of these changes alters what the tool outputs. Also noted because I had predicted otherwise: the tool does **not** flag a path mentioned inside a docstring, a regular expression or a log message unless the string itself begins with the path (its pattern is anchored at the start of the string), so cases `A3-30` to `A3-32`, which I had marked "expected hard", are handled correctly.
3. **Development phase log (v0 to v1), written before the test half was scored.** Only the development half, the audit labels on it, and the challenge set informed these changes; the test half of both corpora was untouched. Defects found and fixed (each with a regression test in `tests/test_rules.py`): (a) **AG002** flagged zero-argument and timeout-only `join` calls (`thread.join()`, `queue.join()`, `proc.join(timeout=5)`) and did not recognise `keys=`, `right_keys=`, `condition=` or `predicates=` as keys, and treated `sep.join(map(str, xs))` as a DataFrame join; (b) **AG003** flagged path *fragments* (`f"{base}/part/"`, `base + "/sales/"`), URL route strings (`@router.get("/items")`, `APIRouter(prefix="/api")`) and scheme tests (`uri.startswith("file://")`); (c) **AG001** did not treat `slice` as a bound, flagged `gc.collect()` and `F.collect(...)`, and did not follow a bound set on an earlier line (`small = df.limit(5)` then `small.collect()`, within one scope). Development results, v0 then v1: challenge set failures 17 then 10 (all 10 remaining were marked known-hard in advance); model-written scripts, development half: AG001 precision 8/9 then 8/8, recall 8/8 both, AG003 9/9 and 9/9 both; human code, development half, 168 files: AG001 findings 70 then 69, AG002 8 then 3, AG003 38 then 17; audited rule-faithful precision AG001 0.961 then 0.981, AG002 0.143 then 0.000 (of 7 and 2 judged findings), AG003 0.447 then 1.000; audited actionable precision AG001 0.100 then 0.117, AG002 0.000 then 0.000, AG003 0.184 then 0.412; metamorphic stability 168/168 under all four transformations for both versions. **Not fixed, and why:** AG002's remaining findings on human code are RDD key joins and Polars list-expression joins, which cannot be told from a keyless DataFrame join without types; AG001's low actionable precision comes from tutorial prints, one-row assertions and library conversion adapters, which is a severity and context question, not a detection defect. **A cost of one fix:** recognising `keys=` stopped flagging one cross-join emulation that uses a constant dummy key (judged rule-faithful by me); on this evidence it is an acceptable trade but it means v1 is slightly less sensitive for that form. v1 is frozen at the commit tagged `v1-after-dev`.
