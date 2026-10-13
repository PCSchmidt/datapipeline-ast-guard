"""Evaluation harness for docs/PROTOCOL.md.

    python scripts/evaluate.py challenge [--rules REV]            # score the constructed challenge set C
    python scripts/evaluate.py run --corpus generated|human --split dev|test [--rules REV] --out FILE
    python scripts/evaluate.py audit --split dev|test             # draw the random audit sample of findings on H
    python scripts/evaluate.py score-generated --split dev|test [--rules REV]   # precision/recall vs blind labels
    python scripts/evaluate.py score-audit --split dev|test [--rules REV]        # precision from audit labels
    python scripts/evaluate.py metamorphic --corpus generated|human --split dev|test [--rules REV]

`--rules REV` loads rules.py from a git revision (for example the tag `v0-as-shipped`) so that the shipped and the
fixed versions can be scored in the same run; without it the working-tree package is used.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "corpus" / "challenge"))

RESULTS = ROOT / "results"


def load_rules(rev: str | None) -> ModuleType:
    if rev is None:
        from datapipeline_ast_guard import rules

        return rules
    src = subprocess.run(
        ["git", "show", f"{rev}:src/datapipeline_ast_guard/rules.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    ).stdout
    tmp = RESULTS / f"_rules_{hashlib.sha256(rev.encode()).hexdigest()[:8]}.py"
    RESULTS.mkdir(exist_ok=True)
    tmp.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"rules_{rev}", tmp)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def spans(source: str) -> dict[tuple[int, int], int]:
    """(line, col) of every Call / Constant node -> its end line, so a label anywhere in a chain can match."""
    out: dict[tuple[int, int], int] = {}
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return out
    for node in ast.walk(tree):
        if isinstance(node, (ast.Call, ast.Constant)) and hasattr(node, "end_lineno"):
            out[(node.lineno, node.col_offset)] = node.end_lineno or node.lineno
    return out


def analyse(rules: ModuleType, source: str, path: str) -> list[dict[str, Any]]:
    sp = spans(source)
    return [
        {
            "rule": f.rule_id,
            "line": f.line,
            "col": f.col,
            "end_line": sp.get((f.line, f.col), f.line),
        }
        for f in rules.analyze_source(source, path)
    ]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def match(labels: list[dict[str, Any]], findings: list[dict[str, Any]]) -> tuple[int, int, int]:
    """Greedy one-to-one matching of label (rule, line) to a finding whose span covers that line."""
    used: set[int] = set()
    tp = 0
    for lab in labels:
        for i, f in enumerate(findings):
            if (
                i not in used
                and f["rule"] == lab["rule"]
                and f["line"] <= lab["line"] <= f["end_line"]
            ):
                used.add(i)
                tp += 1
                break
    return tp, len(findings) - tp, len(labels) - tp


# ------------------------------------------------------------------------------------ challenge set C


def cmd_challenge(rev: str | None) -> None:
    from cases import CASES

    rules = load_rules(rev)
    by_rule: dict[str, Counter[str]] = defaultdict(Counter)
    by_form: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    misses: list[dict[str, Any]] = []
    for case in CASES:
        found = analyse(rules, case.code, case.id)
        got = {(f["rule"], f["line"]) for f in found}
        # a finding on a later line of a multi-line chain still counts for an expectation on any line of its span
        exp = case.expected()
        if case.rule == "AG000" and not case.form.startswith("parses"):
            # an unparseable snippet must yield exactly one AG000 finding and nothing else (any line)
            n_ag000 = sum(1 for f in found if f["rule"] == "AG000")
            if len(found) == 1 and n_ag000 == 1:
                tp, fp, fn = 1, 0, 0
            else:
                tp, fp, fn = (
                    0,
                    len(found) - n_ag000 + max(0, n_ag000 - 1),
                    (1 if n_ag000 == 0 else 0),
                )
        else:
            tp, fp, fn = match([{"rule": r, "line": ln} for r, ln in sorted(exp)], found)
        status = "unclear" if case.unclear else ("ok" if fp == 0 and fn == 0 else "wrong")
        by_rule[case.rule][status] += 1
        by_form[(case.rule, case.form)][status] += 1
        if status == "wrong" or case.hard:
            misses.append(
                {
                    "id": case.id,
                    "rule": case.rule,
                    "form": case.form,
                    "status": status,
                    "expected_hard": case.hard,
                    "tp": tp,
                    "fp": fp,
                    "fn": fn,
                    "found": sorted(got),
                }
            )
    out = {
        "rules_rev": rev or "working-tree",
        "cases": len(CASES),
        "by_rule": {r: dict(c) for r, c in by_rule.items()},
        "wrong_or_hard": misses,
    }
    path = RESULTS / f"challenge_{rev or 'working-tree'}.json"
    RESULTS.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(
        json.dumps(
            {"rules_rev": out["rules_rev"], "cases": out["cases"], "by_rule": out["by_rule"]},
            indent=1,
        )
    )
    for m in misses:
        flag = (
            "HARD(expected)"
            if m["expected_hard"] and m["status"] == "wrong"
            else ("UNEXPECTED" if m["status"] == "wrong" else "hard-but-ok")
        )
        print(
            f"  {m['id']:7s} {m['form']:30s} {m['status']:7s} {flag}  tp={m['tp']} fp={m['fp']} fn={m['fn']}"
        )


# ------------------------------------------------------------------------------------ corpora


def corpus_files(corpus: str, split: str) -> list[dict[str, Any]]:
    """Each item: id, path (local), meta."""
    tasks = {
        t["id"]: t for t in json.loads((ROOT / "corpus" / "tasks.json").read_text(encoding="utf-8"))
    }
    items: list[dict[str, Any]] = []
    if corpus == "generated":
        for line in (
            (ROOT / "corpus" / "manifest_generated.jsonl").read_text(encoding="utf-8").splitlines()
        ):
            r = json.loads(line)
            half = "dev" if hashlib.sha256(r["task"].encode()).digest()[0] % 2 == 0 else "test"
            if half != split:
                continue
            p = ROOT / "corpus" / "generated" / f"{r['task']}__{r['model_tag']}.py"
            items.append(
                {
                    "id": f"{r['task']}__{r['model_tag']}",
                    "path": p if r["ok"] and p.exists() else None,
                    "framework": tasks[r["task"]]["framework"],
                    "model": r["model_tag"],
                }
            )
    elif corpus in ("fresh", "fresh2"):  # docs/PROTOCOL_V2.md, V3.md: one sample, no development/test split
        for line in (ROOT / "corpus" / f"manifest_{corpus}.jsonl").read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            p = ROOT / "corpus" / corpus / r["repo"].replace("/", "__") / r["path"]
            items.append(
                {
                    "id": f"{r['repo']}:{r['path']}",
                    "path": p,
                    "framework": r["stratum"],
                    "repo": r["repo"],
                    "lines": r["lines"],
                }
            )
    else:
        for line in (
            (ROOT / "corpus" / "manifest_human.jsonl").read_text(encoding="utf-8").splitlines()
        ):
            r = json.loads(line)
            if r["split"] != split:
                continue
            p = ROOT / "corpus" / "human" / r["repo"].replace("/", "__") / r["path"]
            items.append(
                {
                    "id": f"{r['repo']}:{r['path']}",
                    "path": p,
                    "framework": r["stratum"],
                    "repo": r["repo"],
                    "lines": r["lines"],
                }
            )
    return items


def cmd_run(corpus: str, split: str, rev: str | None, out: Path) -> None:
    rules = load_rules(rev)
    results = []
    t0 = time.perf_counter()
    total_lines = 0
    for it in corpus_files(corpus, split):
        if it["path"] is None:
            results.append(
                {**{k: v for k, v in it.items() if k != "path"}, "missing": True, "findings": []}
            )
            continue
        src = it["path"].read_text(encoding="utf-8", errors="replace")
        total_lines += src.count("\n") + 1
        results.append(
            {
                **{k: v for k, v in it.items() if k != "path"},
                "missing": False,
                "findings": analyse(rules, src, it["id"]),
            }
        )
    secs = time.perf_counter() - t0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "rules_rev": rev or "working-tree",
                "corpus": corpus,
                "split": split,
                "seconds": secs,
                "lines": total_lines,
                "files": results,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(
        f"{corpus}/{split} [{rev or 'working-tree'}]: {len(results)} files, {total_lines} lines, {secs:.2f}s -> {out}"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("challenge")
    p.add_argument("--rules", default=None)
    p = sub.add_parser("run")
    p.add_argument("--corpus", choices=["generated", "human", "fresh", "fresh2"], required=True)
    p.add_argument("--split", choices=["dev", "test", "all"], required=True)
    p.add_argument("--rules", default=None)
    p.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    if a.cmd == "challenge":
        cmd_challenge(a.rules)
    elif a.cmd == "run":
        cmd_run(a.corpus, a.split, a.rules, a.out)
    random.seed(0)


if __name__ == "__main__":
    main()
