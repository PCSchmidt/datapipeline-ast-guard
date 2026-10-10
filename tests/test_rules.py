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


def test_bare_collect_and_topandas_flagged() -> None:
    assert ids("rows = df.collect()") == ["AG001"]
    assert ids("pdf = df.filter(x).toPandas()") == ["AG001"]


def test_limit_before_collect_ok() -> None:
    assert ids("rows = df.limit(10).collect()") == []
    assert ids("rows = lf.filter(x).head(5).collect()") == []


def test_cross_join_and_missing_keys() -> None:
    assert ids("a.crossJoin(b)") == ["AG002"]
    assert ids("a.join(b)") == ["AG002"]
    assert ids("a.join(b, how='cross')") == ["AG002"]
    assert ids("a.join(b, 'id')") == []
    assert ids("a.join(b, on='id', how='left')") == []
    assert ids("a.join(b, a.id == b.id)") == []


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
    assert doc["version"] == "2.1.0" and res["ruleId"] == "AG001" and res["level"] == "error"
    assert res["locations"][0]["physicalLocation"]["region"]["startLine"] == 1


def test_cli_exit_codes(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text("df.collect()\n")
    (tmp_path / "ok.py").write_text("df.limit(1).collect()\n")
    (tmp_path / "warn.py").write_text("open('/data/x.csv')\n")
    runner = CliRunner()
    assert runner.invoke(main, [str(tmp_path / "ok.py")]).exit_code == 0
    assert runner.invoke(main, [str(tmp_path / "warn.py")]).exit_code == 0
    assert runner.invoke(main, [str(tmp_path / "bad.py")]).exit_code == 1
    assert runner.invoke(main, [str(tmp_path), "--format", "sarif"]).exit_code == 1


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
    assert ids("orders.join(customers)") == ["AG002"]
