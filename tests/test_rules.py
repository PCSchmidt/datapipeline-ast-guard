from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from hypothesis import given
from hypothesis import strategies as st

from datapipeline_ast_guard import analyze_source, to_sarif
from datapipeline_ast_guard.cli import main


def ids(src: str) -> list[str]:
    return [f.rule_id for f in analyze_source(src)]


SPARK = "import pyspark\n"  # AG002 only reports joins in files that import a dataframe library (v2)


def test_bare_collect_and_topandas_flagged() -> None:
    assert ids("rows = df.collect()") == ["AG001"]
    assert ids("pdf = df.filter(x).toPandas()") == ["AG001"]


def test_limit_before_collect_ok() -> None:
    assert ids("rows = df.limit(10).collect()") == []
    assert ids("rows = lf.filter(x).head(5).collect()") == []


def test_cross_join_and_missing_keys() -> None:
    assert ids(SPARK + "a.crossJoin(b)") == ["AG002"]
    assert ids(SPARK + "a.join(b)") == ["AG002"]
    assert ids(SPARK + "a.join(b, how='cross')") == ["AG002"]
    assert ids(SPARK + "a.join(b, 'id')") == []
    assert ids(SPARK + "a.join(b, on='id', how='left')") == []
    assert ids(SPARK + "a.join(b, a.id == b.id)") == []


def test_hardcoded_paths() -> None:
    assert ids("spark.read.parquet('s3://bucket/x')") == ["AG003"]
    assert ids("open('/data/in.csv')") == ["AG003"]
    assert ids("open('C:\\\\data\\\\in.csv')") == ["AG003"]
    assert ids("x = 'not/a path'") == []
    assert ids("open(os.environ['IN'])") == []


def test_inline_suppression_is_rule_specific() -> None:
    assert ids("df.collect()  # ast-guard: ignore[AG001]") == []
    assert ids("df.collect()  # ast-guard: ignore[AG002]") == ["AG001"]


def test_syntax_error_is_critical_not_crash() -> None:
    (f,) = analyze_source("def (:")
    assert f.rule_id == "AG000" and f.severity.value == "critical"


def test_sarif_shape() -> None:
    doc = json.loads(to_sarif(analyze_source("df.collect()", "a/b.py")))
    res = doc["runs"][0]["results"][0]
    assert doc["version"] == "2.1.0" and res["ruleId"] == "AG001" and res["level"] == "warning"
    assert res["locations"][0]["physicalLocation"]["region"]["startLine"] == 1


def test_cli_exit_codes(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text("import pyspark\na.crossJoin(b)\n")
    (tmp_path / "ok.py").write_text("df.limit(1).collect()\n")
    (tmp_path / "warn.py").write_text("open('/data/x.csv')\ndf.collect()\n")
    runner = CliRunner()
    assert runner.invoke(main, [str(tmp_path / "ok.py")]).exit_code == 0
    assert runner.invoke(main, [str(tmp_path / "warn.py")]).exit_code == 0
    assert runner.invoke(main, [str(tmp_path / "bad.py")]).exit_code == 1
    assert runner.invoke(main, [str(tmp_path), "--format", "sarif"]).exit_code == 1
    # --fail-on: warnings can gate too, and `never` reports without failing
    assert runner.invoke(main, [str(tmp_path / "warn.py"), "--fail-on", "warning"]).exit_code == 1
    assert runner.invoke(main, [str(tmp_path / "bad.py"), "--fail-on", "never"]).exit_code == 0


@given(st.text(max_size=300))
def test_never_raises_on_arbitrary_text(src: str) -> None:
    for f in analyze_source(src):
        assert f.line >= 1


def test_string_and_path_joins_are_not_dataframe_joins() -> None:
    # Regression: ordinary Python joins were flagged as keyless DataFrame joins (critical).
    assert ids("x = ', '.join(names)") == []
    assert ids("x = f'{a}-'.join(parts)") == []
    assert ids("p = os.path.join(a)") == []
    assert ids("x = sep.join([a, b])") == []
    assert ids("x = sep.join(str(i) for i in xs)") == []
    # still flagged: a bare receiver with a bare argument is indistinguishable from a DataFrame join
    assert ids(SPARK + "orders.join(customers)") == ["AG002"]


# ---- regression tests for defects found on the development half of the evaluation (docs/PROTOCOL.md) ----


def test_thread_and_queue_joins_are_not_dataframe_joins() -> None:
    assert ids("worker.join()") == []
    assert ids("worker.join(timeout=5)") == []
    assert ids("jobs.join()") == []
    assert ids(SPARK + "a.join(other=b)") == [
        "AG002"
    ]  # a DataFrame join given by keyword is still keyless


def test_alternative_key_keywords_count_as_keys() -> None:
    assert ids("t.join(u, keys=['id'], right_keys=['id'])") == []
    assert ids("rel.join(other, condition=c, how='inner')") == []
    assert ids("t.join(u, predicates=p)") == []
    assert ids("t.join(u, right_on='k', left_on='k')") == []


def test_join_of_a_builtin_iterator_is_a_string_join() -> None:
    assert ids("text = sep.join(map(str, xs))") == []
    assert ids("text = sep.join(sorted(names))") == []
    assert ids(SPARK + "text = sep.join(parts)") == [
        "AG002"
    ]  # still ambiguous without types (documented)


def test_path_fragments_are_not_hardcoded_paths() -> None:
    assert ids("p = f'{base}/part/x.csv'") == []
    assert ids("p = base + '/sales/'") == []
    assert ids("p = f'/data/{day}/x.csv'") == ["AG003"]  # the f-string begins with the path
    assert ids("p = '/data/in' + suffix") == ["AG003"]  # the path is the left, constant operand
    assert ids("def run(path='/data/in'):\n    return path") == [
        "AG003"
    ]  # argument defaults are checked


def test_routes_and_scheme_tests_are_not_paths() -> None:
    assert ids("@router.get('/items/{item_id}')\ndef f(item_id):\n    return item_id") == []
    assert ids("router = APIRouter(prefix='/api/items')") == []
    assert ids("if uri.startswith('file://'):\n    pass") == []
    assert ids("if uri.endswith('/data/x'):\n    pass") == []
    assert ids("open('/data/in.csv')") == ["AG003"]


def test_slice_bounds_a_chain() -> None:
    assert ids("frame = lf.slice(0, 100).collect()") == []


def test_gc_and_functions_alias_collect_are_not_dataset_materialisation() -> None:
    assert ids("import gc\ngc.collect()") == []
    assert ids("x = F.collect(col)") == []
    assert ids("rows = df.collect()") == ["AG001"]


def test_a_bound_on_an_earlier_statement_is_tracked_within_a_scope() -> None:
    assert ids("small = df.limit(5)\nrows = small.collect()") == []
    assert ids("small = df.limit(5)\nagg = small.select('a')\nrows = agg.collect()") == []
    assert ids("small = df.limit(5)\nsmall = df\nrows = small.collect()") == [
        "AG001"
    ]  # reassigned unbounded
    assert ids("def f(df):\n    small = df.limit(5)\n    return small.collect()") == []
    assert ids("small = df.limit(5)\ndef g(df):\n    return small.collect()") == [
        "AG001"
    ]  # other scope
    assert ids("rows = other.collect()") == ["AG001"]


# ---- v2 (docs/PROTOCOL_V2.md): severity and AG002 scope ----


def severities(src: str) -> list[tuple[str, str]]:
    return [(f.rule_id, f.severity.value) for f in analyze_source(src)]


def test_ag001_is_a_warning() -> None:
    assert severities("df.collect()") == [("AG001", "warning")]


def test_keyless_join_is_reported_only_for_pyspark_files_as_a_warning() -> None:
    assert severities("import pyspark\na.join(b)") == [("AG002", "warning")]
    assert severities("from pyspark.sql import functions as F\na.join(b)") == [("AG002", "warning")]
    for lib in ("pandas", "polars", "pyarrow", "duckdb"):
        assert ids(f"import {lib}\na.join(b)") == [], lib  # index join / not the Cartesian hazard
    assert ids("a.join(b)") == []  # no dataframe import: not evidence of a DataFrame


def test_explicit_cross_join_stays_critical_in_any_dataframe_file() -> None:
    assert severities("import pyspark\na.crossJoin(b)") == [("AG002", "critical")]
    assert severities("import polars as pl\na.join(b, how='cross')") == [("AG002", "critical")]
    assert ids("a.crossJoin(b)") == []  # without a dataframe import there is no evidence
