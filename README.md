# datapipeline-ast-guard — a pre-merge safety check for AI-written data pipeline code

![CI](https://github.com/PCSchmidt/datapipeline-ast-guard/actions/workflows/ci.yml/badge.svg)

**Status: v0.4, portfolio project.** Three rules, JSON and SARIF output, CLI and tests are complete, and detection quality has now been measured on real and model-written code ([Results](#results), [docs/RESULTS.md](docs/RESULTS.md)). The honest summary: the rules are accurate and stable, but on real code `AG001` is rarely worth a reviewer's time (so v2 demotes it from critical to a warning) and `AG002` has not been shown to find anything.

```text
$ agent-lint examples/agent_written_pipeline.py          # exit code 1
AG003 warning   line 7   Hard-coded file-system path           spark.read.parquet("s3://prod-data/orders/2026/")
AG003 warning   line 8   Hard-coded file-system path           spark.read.csv("/data/customers.csv", ...)
AG002 warning   line 10  Join without explicit keys           orders.join(customers)
AG002 critical  line 11  Cross join, or join without keys     customers.crossJoin(orders.select("region"))
AG001 warning   line 13  Unbounded collect()/toPandas()       enriched.collect()
```

*Real findings from [examples/agent_written_pipeline.py](examples/agent_written_pipeline.py). The tool itself prints JSON or SARIF (rule, severity, line, column, message); I have reformatted the lines and added the offending source text on the right for readability. Line 14, `enriched.limit(100).toPandas()`, is correctly not flagged.*

## What is this? (plain-language overview)

AI coding assistants now write a lot of data-engineering code: Spark jobs, Polars scripts, SQL glue. That code often looks right and passes a unit test on ten rows, then fails or becomes very expensive on a real cluster. The same few mistakes keep appearing:

- a **join with no keys** (or an explicit cross join) that turns two million rows into four trillion;
- **`.collect()` or `.toPandas()`** on a whole distributed table, which pulls everything into one machine's memory;
- **hard-coded paths** (`s3://prod-data/...`, `/data/customers.csv`) that tie the code to one environment.

datapipeline-ast-guard is a small command-line tool that reads Python files and flags those patterns **without running them**. It parses each file into an abstract syntax tree (the structure Python itself builds), walks the tree looking for the patterns, and reports each finding with an exact line and column. If any finding at or above `--fail-on` (by default, *critical*) exists, the command exits with a non-zero status, which is what makes a CI job fail and a pull request block.

**What it is not.** It is not a type checker, a style linter, or a general code-quality tool, and it does not understand your data. It is a handful of narrow, explainable rules aimed at one failure family.

### Who it is for, and when it earns its place

| If you are... | the tool gives you... |
| --- | --- |
| a team that lets AI assistants open PRs against data pipelines | an automatic gate that stops the classic cluster-killers before review |
| a data engineer reviewing AI-generated code | a short list of lines to look at first |
| building an agent that writes data code | a deterministic check to run on its output **before** anything executes, so a bad generation never has side effects |
| in a regulated or air-gapped environment | a checker with no network access and no model, so results are reproducible and explainable |

It is a poor fit if you need semantic checks (does this join logic match the business rule?), type or schema checking, or coverage of rules beyond the three listed below.

### Why static analysis instead of running the code, or asking an LLM?

Running generated code to see if it is safe is the thing you are trying to avoid. Asking another LLM adds cost, variability and its own blind spots. A syntax-tree rule gives the same answer every time, takes milliseconds, can be unit-tested, and can say exactly which line it objects to and why.

**What's real and what's not.** Everything described here runs today. What is **not** established is how often these rules are right on real agent-written code: the benchmark corpus is not built yet, so there are no precision or recall numbers, and the rules are heuristics with known blind spots (see [Limitations](#limitations)).

## At a glance

| | |
| --- | --- |
| Input | Python files or directories |
| Output | JSON list, or SARIF 2.1.0 (for GitHub code scanning), with rule id, severity, file, line, column |
| Exit code | 1 if a finding at or above `--fail-on` exists: `critical` (default), `warning` or `never`. Critical findings are an explicit cross join and an unparseable file |
| Rules | AG000 unparseable file, AG001 unbounded collect, AG002 cross join or keyless join, AG003 hard-coded path |
| Suppression | `# ast-guard: ignore[AG001]` on the line, rule-specific |
| Dependencies | Python 3.11+, `click`; no network, no model |
| Tests | 10, including a property-based test that arbitrary text never crashes the analyser; `mypy --strict`; ruff |

## Architecture at a glance

```mermaid
flowchart LR
    CODE[/"LLM-written pipeline<br>.py files"/]
    subgraph parse["1 · Parse, never execute"]
        direction TB
        AST["ast.parse<br>no import, no eval"]
        BAD["AG000 critical<br>file does not parse"]
    end
    subgraph rules["2 · Rule passes (AST visitors)"]
        direction TB
        R1["AG001 warning<br>collect / toPandas<br>with no limit in the chain"]
        R2["AG002 cross join: critical<br>keyless join (PySpark): warning"]
        R3["AG003 warning<br>hard-coded path or URI"]
    end
    subgraph filt["3 · Filter"]
        SUP["drop findings on lines marked<br>ast-guard: ignore[RULE]<br>rule-specific"]
    end
    subgraph out["4 · Report"]
        direction TB
        FMT["JSON or SARIF 2.1.0<br>exact line + column"]
        EXIT{"any critical?"}
        BLOCK(["exit 1<br>CI blocks the PR"])
        PASS(["exit 0"])
    end
    CODE --> AST
    AST -- "syntax error" --> BAD
    AST -- "tree" --> R1 & R2 & R3
    R1 & R2 & R3 --> SUP --> FMT --> EXIT
    BAD --> FMT
    EXIT -- "yes" --> BLOCK
    EXIT -- "no" --> PASS
    classDef det fill:#e8f1fb,stroke:#2f6db5,color:#102a43
    classDef bad fill:#fde8e8,stroke:#c0392b,color:#4a1010
    classDef ok fill:#e3f5e8,stroke:#2e8b57,color:#0f3b21
    classDef io fill:#f2f2f2,stroke:#666,color:#222
    class AST,R1,R2,R3,SUP,FMT,EXIT det
    class BAD,BLOCK bad
    class PASS ok
    class CODE io
    style parse fill:#f4f8fd,stroke:#2f6db5,color:#102a43
    style rules fill:#f4f8fd,stroke:#2f6db5,color:#102a43
    style filt fill:#f4f8fd,stroke:#2f6db5,color:#102a43
    style out fill:#f4f8fd,stroke:#2f6db5,color:#102a43
```

*Everything here is deterministic: there is no model anywhere in the tool. That is the point: it is the check you put in front of the probabilistic code-writer.*

## Quickstart

```bash
git clone https://github.com/PCSchmidt/datapipeline-ast-guard && cd datapipeline-ast-guard
uv venv && uv pip install -e ".[dev]"

agent-lint examples/agent_written_pipeline.py                 # JSON, exit 1
agent-lint src/pipelines --format sarif > guard.sarif         # SARIF for code scanning
pytest -q                                                     # 24 passed
```

As a CI step (GitHub Actions):

```yaml
- run: pip install datapipeline-ast-guard      # not on PyPI yet: use `pip install git+https://github.com/PCSchmidt/datapipeline-ast-guard`
- run: agent-lint pipelines/ --format sarif > guard.sarif
- uses: github/codeql-action/upload-sarif@v3
  if: always()
  with: { sarif_file: guard.sarif }
```

Suppress a reviewed line: `rows = small_df.collect()  # ast-guard: ignore[AG001]`. Suppression is per rule, so it can never hide a different problem on the same line.

## Approach: why it is built this way

- **Parse, don't run.** The tool never imports or executes the code it checks, so an unsafe generation cannot do harm while being checked.
- **Narrow rules, each explainable in one sentence.** A finding you cannot explain is a finding people learn to ignore.
- **Fail closed on broken input.** A file that does not parse is a *critical* finding (AG000), not a skipped file.
- **Severity means something.** Critical blocks the merge; a warning informs and does not (unless you pass `--fail-on warning`). Since v2, `AG001` is a warning because the measured evidence did not support blocking on it.
- **Standard output formats.** JSON for scripts, SARIF 2.1.0 so GitHub code scanning can show findings inline on the PR.

## Motivation

This is the "deterministic gate in front of a probabilistic generator" idea applied to data-engineering code. My background includes enterprise PySpark and Pandas pipeline delivery, and the failure modes above are the ones that matter most there. The tool is deliberately small: the aim was a trustworthy first gate, not a complete linter.

## Method (what the tool actually does)

1. **Parse** each file with `ast.parse`. A syntax error becomes one AG000 finding for that file and the run continues.
2. **Walk the tree** with a single visitor:
   - *AG001*: for every call named `collect`, `toPandas` or `to_pandas`, look at the method names earlier in the same call chain; flag it (as a warning) unless one of `limit`, `head`, `take`, `first`, `sample`, `fetch`, `slice` is present in the chain or was assigned to the same name earlier in the scope.
   - *AG002*: in files that import a dataframe library, flag `crossJoin` and `how="cross"` as critical; in files that import `pyspark`, also flag `.join(other)` with no key keyword and no second positional argument, as a warning (in pandas such a join is an index join and Polars requires `on`).
   - *AG003*: flag string literals that look like an absolute path (`/dir/file`, `C:\...`) or a URI with scheme `s3`, `s3a`, `gs`, `abfs`, `abfss`, `hdfs`, `dbfs` or `file`.
3. **Apply suppressions**: drop a finding if its own line carries `# ast-guard: ignore[...]` naming that rule.
4. **Report** sorted by line, as JSON or SARIF, and exit 1 if a finding at or above `--fail-on` (default `critical`) exists.

## Results

Pre-registered ([docs/PROTOCOL.md](docs/PROTOCOL.md)), scored once on held-out halves, full numbers and caveats in [docs/RESULTS.md](docs/RESULTS.md). v0 is the tool as first shipped, v1 the version after fixes made on development data only. One rater (the author), a convenience sample of 300 real files from 83 public repositories, and 27 labelled model-written positives: treat everything as small-sample.

- **Noise on real code.** v0 flags 27% of real PySpark, Polars and pandas files (95% interval 21 to 34%); v1 flags 25%. About 12 ms per 1,000 lines.
- **`AG001` (unbounded collect):** 97% of findings are what the rule describes, but only about 1 in 10 was something a reviewer would want to look at (3/44 on the test half). As a critical, merge-blocking rule it would mostly be noise on code like this, which is why v1 measured it and v2 demotes it to a warning.
- **`AG002` (keyless join):** one rule-faithful case in 15 audited findings. Most false alarms (thread and pool joins, string joins, unrecognised key keywords) are removed in v1, but the rule has not been shown to find a real keyless DataFrame join.
- **`AG003` (hard-coded path):** v0 was 0.58 precise because it matched path fragments in f-strings and route strings; v1 reaches 0.94 on unseen repositories, but only about 1 in 34 findings was actionable.
- **Model-written scripts:** every labelled `AG001` and `AG003` positive was found (12/12, 15/15), unparseable scripts were caught as `AG000`; there were no `AG002` positives to score.
- **Robustness:** findings were identical under reformatting, local renaming, added comments and wrapping in a function, on all real and parseable model-written files.

**v2 (severity and `AG002` scope), re-measured on 288 files from 116 repositories nobody had read** ([docs/PROTOCOL_V2.md](docs/PROTOCOL_V2.md), [docs/RESULTS_V2.md](docs/RESULTS_V2.md)): the default gate fails 20.8% of files under v1 and 0 for a real finding under v2 (2.1% in all, the unparseable files). The noise itself is not smaller, it no longer blocks. `AG003` precision on unseen code was 0.83, not the 0.94 measured earlier, and a new false-alarm class (parameter names and URL routes that look like paths) was found and not fixed. `AG002` found no real defect in either study.

**v3 (`AG003` no longer reports parameter-store names, HTTP routes and API prefixes), checked on 223 more unseen files** ([docs/PROTOCOL_V3.md](docs/PROTOCOL_V3.md), [docs/RESULTS_V3.md](docs/RESULTS_V3.md)): `AG003` rule-faithful precision 0.87 to 0.90 (the fix removed its two targets and no real path), actionable precision 0.15; new false-alarm kinds (MLflow experiment names, concatenated parameter names, regular expressions) were found and not fixed. **Recall by mutation** (injecting a keyless join, a cross join, an unbounded `collect()` or a hard-coded path into real files) found every injected defect in the plain forms (up to 100/100), with no side effects; this is a sanity check on the plain forms, not an estimate of recall in the wild.

Also verified: 24 unit and property-based tests, `mypy --strict` and ruff clean, and the Docker image builds and passes its tests offline.

## Limitations

- **Heuristics, no types.** Receiver types are unknown, so a non-DataFrame object with a `.collect()` method is flagged. AG002 skips string-literal receivers, `os.path.join` and list/generator arguments, but `sep.join(parts)` (a variable receiver with a variable argument) looks exactly like a DataFrame join and **is flagged**; suppress it with the comment.
- **Limited bound tracking.** v1 tracks a name assigned from a bounded chain within one scope (`small = df.limit(5)` then `small.collect()`), but not bounds across functions, containers or reassignment through other calls; use the suppression comment where the bound is real.
- **Only three rules.** Not covered: unpartitioned shuffles, null-unsafe join keys, missing schema assertions after JSON ingestion, SQL (`sqlglot`) rules, and property-based schema-invariance checks.
- **Join keys are not validated.** AG002 checks that keys are given, not that they are the right ones.
- **Paths in comments and docstrings** that look like paths can raise a warning.
- **Low actionable precision on real code.** Measured on a convenience sample: roughly 1 in 10 `AG001` findings and 1 in 30 `AG003` findings were worth a reviewer's time, and, on this evidence, blocking merges on `AG001` is hard to justify (hence the v2 demotion). On code never seen before, `AG001` actionable precision was 0.17 and `AG003` 0.23. `AG002` is unproven on real code, and recall on real code was not measured.
- **Not on PyPI yet.**

## Known gaps against the original roadmap

The project began as an item in a longer roadmap that named a larger stack and scope. These parts of that plan were **not built**; the results above say nothing about them.

- SQL analysis with `sqlglot` and DuckDB SQL rules.
- Checks for unpartitioned shuffles, missing broadcast hints, null-unsafe join keys, and missing schema assertions after nested JSON ingestion.
- Property-based verification (with `hypothesis`) that a generated transformation keeps its schema: `hypothesis` is used to test the tool, not the analysed code.
- A packaged, reusable GitHub Action: the README shows how to run the CLI as a CI step.

## Operational notes

### What runs where

A local command-line tool or a CI step. No server, no network access, no model, no credentials.

### Data and keys

No keys. The analysed source is read from disk and never leaves the machine. Nothing is stored.

### Verify the claims (a reviewer's path)

```bash
pytest -q                                              # 24 passed
mypy src tests                                         # strict, clean
agent-lint examples/agent_written_pipeline.py; echo $? # the findings above, then 1
docker build -t ast-guard . && docker run --rm --network none ast-guard   # tests offline
```

### Documentation map

| Doc | What it covers |
| --- | --- |
| [docs/PROTOCOL.md](docs/PROTOCOL.md) | the pre-registered evaluation plan, with logged deviations |
| [docs/RESULTS.md](docs/RESULTS.md) | measured results for v0 and v1, caveats and limits |
| [docs/PROTOCOL_V2.md](docs/PROTOCOL_V2.md), [docs/RESULTS_V2.md](docs/RESULTS_V2.md) | the v2 severity change, pre-registered and re-measured on unseen repositories |
| [docs/PROTOCOL_V3.md](docs/PROTOCOL_V3.md), [docs/RESULTS_V3.md](docs/RESULTS_V3.md) | the v3 `AG003` fix on a third unseen sample, and recall by mutation |
| [examples/agent_written_pipeline.py](examples/agent_written_pipeline.py) | the sample used in the output above |
| [src/datapipeline_ast_guard/rules.py](src/datapipeline_ast_guard/rules.py) | every rule, in about 120 lines |

## License

MIT. See [LICENSE](LICENSE).

## Author

Chris Schmidt ([PCSchmidt](https://github.com/PCSchmidt)). Part of a portfolio on evaluator-gated AI systems: probabilistic components propose, deterministic gates decide.
