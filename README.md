# datapipeline-ast-guard

Static guardrails for LLM-generated PySpark / Polars code. The script is **parsed, never executed**, so a bad generation cannot have side effects before it is checked. Output is JSON or SARIF 2.1.0 with exact line numbers; any critical finding exits non-zero so CI can block the pull request.

**Status:** v0.1 scaffold. Three rules implemented and tested; false-positive/negative rates on real agent-authored pipelines are **not yet measured** (see [docs/RESULTS.md](docs/RESULTS.md)).

## Rules

| Id | Severity | Flags |
|---|---|---|
| AG000 | critical | file does not parse |
| AG001 | critical | `.collect()` / `.toPandas()` / `.to_pandas()` with no `limit/head/take/first/sample/fetch` earlier in the same call chain |
| AG002 | critical | `crossJoin`, `how="cross"`, or `.join(other)` with no keys |
| AG003 | warning | string literal that is an absolute path or `s3://`, `gs://`, `hdfs://`, `dbfs:/`, `abfs://`, `file://` URI |

Suppress one line with `# ast-guard: ignore[AG001]` (rule-specific, so a suppression never hides a different rule).

## Use

```bash
uv pip install -e ".[dev]"
agent-lint src/pipelines --format sarif > guard.sarif   # exit 1 on critical findings
```

GitHub Action step:

```yaml
- run: pip install datapipeline-ast-guard
- run: agent-lint pipelines/ --format sarif > guard.sarif
- uses: github/codeql-action/upload-sarif@v3
  if: always()
  with: { sarif_file: guard.sarif }
```

## Checks

```bash
pytest          # unit + hypothesis (arbitrary text never crashes the analyser)
mypy src tests  # strict
docker build -t ast-guard . && docker run --rm --network none ast-guard
```

## Limits (heuristics, by design)

- Chain analysis is syntactic: a limit applied on an earlier statement (`small = df.limit(5)` then `small.collect()`) is not tracked, so AG001 fires. Use the suppression comment where the bound is real.
- Receiver types are unknown; a non-DataFrame object with a `.collect()` method is flagged.
- Not covered yet: unpartitioned shuffles, null-unsafe join keys, schema assertions after JSON ingestion, SQL (`sqlglot`) rules, and `hypothesis`-generated schema-invariance checks from the roadmap.
