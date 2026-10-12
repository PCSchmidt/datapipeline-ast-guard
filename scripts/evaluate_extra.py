"""Scoring, audit and metamorphic commands for the evaluation harness (see scripts/evaluate.py and docs/PROTOCOL.md).

python scripts/evaluate_extra.py score-generated --split dev|test [--rules REV]
python scripts/evaluate_extra.py audit --split dev|test [--rules REV] [--show START COUNT]
python scripts/evaluate_extra.py score-audit --split dev|test [--rules REV]
python scripts/evaluate_extra.py metamorphic --corpus generated|human --split dev|test [--rules REV]
"""

from __future__ import annotations

import argparse
import ast
import builtins
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from evaluate import RESULTS, ROOT, analyse, corpus_files, load_rules, match, wilson

LABELS_GENERATED = ROOT / "corpus" / "labels_generated.json"
LABELS_AUDIT = ROOT / "corpus" / "labels_audit.json"
RULES = ("AG001", "AG002", "AG003")


def fmt(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} [{lo:.3f}, {hi:.3f}]" if n else "n/a (0)"


# ------------------------------------------------------------------------------------ generated corpus G


def cmd_score_generated(split: str, rev: str | None) -> None:
    rules = load_rules(rev)
    labels: dict[str, Any] = json.loads(LABELS_GENERATED.read_text(encoding="utf-8"))
    tot: dict[str, Counter[str]] = {r: Counter() for r in RULES}
    per_model: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: {r: Counter() for r in RULES}
    )
    per_framework: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: {r: Counter() for r in RULES}
    )
    ag000 = Counter()
    errors: list[dict[str, Any]] = []
    actionable = Counter()
    for it in corpus_files("generated", split):
        lab = labels.get(it["id"])
        if lab is None:
            raise SystemExit(f"no label for {it['id']}: label every script before scoring")
        if it["path"] is None:
            ag000["missing_generation"] += 1
            continue
        src = it["path"].read_text(encoding="utf-8", errors="replace")
        found = analyse(rules, src, it["id"])
        parses = not any(f["rule"] == "AG000" for f in found)
        ag000[
            (
                "tp"
                if not lab["parses"] and not parses
                else "fp"
                if lab["parses"] and not parses
                else "fn"
                if not lab["parses"] and parses
                else "tn"
            )
        ] += 1
        if not parses:
            continue
        for rule in RULES:
            pos = [p for p in lab["positives"] if p["rule"] == rule]
            fnd = [f for f in found if f["rule"] == rule]
            tp, fp, fn = match(pos, fnd)
            for d in (
                tot[rule],
                per_model[it["model"]][rule],
                per_framework[it["framework"]][rule],
            ):
                d["tp"] += tp
                d["fp"] += fp
                d["fn"] += fn
            actionable[rule] += sum(1 for p in pos if p.get("actionable"))
            if fp or fn:
                errors.append(
                    {
                        "id": it["id"],
                        "rule": rule,
                        "fp": fp,
                        "fn": fn,
                        "found": [f["line"] for f in fnd],
                        "labelled": [p["line"] for p in pos],
                    }
                )
    print(f"== generated/{split} [{rev or 'working-tree'}]")
    for rule in RULES:
        c = tot[rule]
        print(
            f"{rule}: precision {fmt(c['tp'], c['tp'] + c['fp'])} | recall {fmt(c['tp'], c['tp'] + c['fn'])} | labelled positives that are actionable {actionable[rule]}"
        )
    print("AG000 (unparseable scripts):", dict(ag000))
    for name, table in (("model", per_model), ("framework", per_framework)):
        for key, per in sorted(table.items()):
            print(
                f"  by {name} {key}: "
                + "; ".join(
                    f"{r} p={per[r]['tp']}/{per[r]['tp'] + per[r]['fp']} r={per[r]['tp']}/{per[r]['tp'] + per[r]['fn']}"
                    for r in RULES
                )
            )
    out = RESULTS / f"generated_{split}_{rev or 'working-tree'}.json"
    out.write_text(
        json.dumps(
            {"totals": {r: dict(tot[r]) for r in RULES}, "ag000": dict(ag000), "errors": errors},
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"errors ({len(errors)}) written to {out}")


# ------------------------------------------------------------------------------------ audit on human code H


def audit_sample(split: str, rev: str | None) -> list[dict[str, Any]]:
    rules = load_rules(rev)
    by_rule: dict[str, list[dict[str, Any]]] = {r: [] for r in RULES}
    for it in corpus_files("human", split):
        src = it["path"].read_text(encoding="utf-8", errors="replace")
        for f in analyse(rules, src, it["id"]):
            if f["rule"] in by_rule:
                by_rule[f["rule"]].append(
                    {
                        "fid": f"{f['rule']}|{it['id']}|{f['line']}",
                        "rule": f["rule"],
                        "file": it["id"],
                        "path": str(it["path"]),
                        "line": f["line"],
                        "end_line": f["end_line"],
                        "stratum": it["framework"],
                    }
                )
    rng = random.Random(0)
    sample: list[dict[str, Any]] = []
    for rule, rows in by_rule.items():
        rows.sort(key=lambda r: r["fid"])
        rng.shuffle(rows)
        sample += rows[:60]
        print(f"{rule}: {len(rows)} findings in {split}; auditing {min(60, len(rows))}")
    return sample


def cmd_audit(split: str, rev: str | None, show: tuple[int, int] | None) -> None:
    sample = audit_sample(split, rev)
    path = ROOT / "corpus" / f"audit_{split}_{rev or 'working-tree'}.json"
    path.write_text(
        json.dumps([{k: v for k, v in s.items() if k != "path"} for s in sample], indent=1),
        encoding="utf-8",
    )
    print(f"sample ({len(sample)} findings) written to {path}")
    if show:
        start, count = show
        for i, s in enumerate(sample[start : start + count], start=start):
            lines = Path(s["path"]).read_text(encoding="utf-8", errors="replace").splitlines()
            lo, hi = max(0, s["line"] - 6), min(len(lines), s["end_line"] + 4)
            print(f"\n#{i} {s['fid']}  [{s['stratum']}]")
            for n in range(lo, hi):
                mark = ">>" if s["line"] - 1 <= n <= s["end_line"] - 1 else "  "
                print(f"{mark}{n + 1:5d} {lines[n][:150]}")


def cmd_score_audit(split: str, rev: str | None) -> None:
    sample = json.loads(
        (ROOT / "corpus" / f"audit_{split}_{rev or 'working-tree'}.json").read_text(
            encoding="utf-8"
        )
    )
    labels: dict[str, Any] = json.loads(LABELS_AUDIT.read_text(encoding="utf-8"))
    print(f"== audit/{split} [{rev or 'working-tree'}]")
    for rule in RULES:
        rows = [s for s in sample if s["rule"] == rule]
        got = [labels[s["fid"]] for s in rows if s["fid"] in labels]
        yes = sum(1 for g in got if g["faithful"] == "yes")
        no = sum(1 for g in got if g["faithful"] == "no")
        unclear = sum(1 for g in got if g["faithful"] == "unclear")
        act_yes = sum(1 for g in got if g["actionable"] == "yes")
        act_no = sum(1 for g in got if g["actionable"] == "no")
        print(
            f"{rule}: labelled {len(got)}/{len(rows)} | rule-faithful precision {fmt(yes, yes + no)} | actionable precision {fmt(act_yes, act_yes + act_no)} | unclear {unclear}"
        )


# ------------------------------------------------------------------------------------ metamorphic stability


def _local_names(tree: ast.AST) -> dict[str, str]:
    imported: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imported |= {(a.asname or a.name).split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            imported |= {a.asname or a.name for a in n.names}
    stores = {
        n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
    }
    stores |= {a.arg for a in ast.walk(tree) if isinstance(a, ast.arg)}
    names = sorted(stores - imported - set(dir(builtins)) - {"self", "cls"})
    return {n: f"v{i}" for i, n in enumerate(names)}


class _Rename(ast.NodeTransformer):
    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping

    def visit_Name(self, node: ast.Name) -> ast.AST:
        node.id = self.mapping.get(node.id, node.id)
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        node.arg = self.mapping.get(node.arg, node.arg)
        return node


def t_unparse(src: str) -> str:
    return ast.unparse(ast.parse(src))


def t_rename(src: str) -> str:
    tree = ast.parse(src)
    return ast.unparse(_Rename(_local_names(tree)).visit(tree))


def t_comments(src: str) -> str:
    tree = ast.parse(src)
    starts = sorted(
        {min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])]) for n in tree.body}
    )
    lines = src.splitlines()
    for ln in reversed(starts):
        lines.insert(ln - 1, "# reviewed: behaviour unchanged")
    return "\n".join(lines) + "\n"


def t_wrap(src: str) -> str:
    tree = ast.parse(src)
    head = [
        n
        for n in tree.body
        if isinstance(n, (ast.Import, ast.ImportFrom))
        or (
            isinstance(n, ast.Expr)
            and isinstance(n.value, ast.Constant)
            and isinstance(n.value.value, str)
        )
    ]
    rest = [n for n in tree.body if n not in head]
    if not rest:
        return src
    fn = ast.FunctionDef(
        name="_wrapped",
        args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=rest,
        decorator_list=[],
        type_params=[],
    )
    new = ast.Module(body=[*head, fn], type_ignores=[])
    ast.fix_missing_locations(new)
    return ast.unparse(new)


TRANSFORMS = {
    "unparse": t_unparse,
    "rename_locals": t_rename,
    "add_comments": t_comments,
    "wrap_in_function": t_wrap,
}


def cmd_metamorphic(corpus: str, split: str, rev: str | None) -> None:
    rules = load_rules(rev)
    stats: dict[str, Counter[str]] = {t: Counter() for t in TRANSFORMS}
    diffs: list[dict[str, Any]] = []
    for it in corpus_files(corpus, split):
        if it["path"] is None:
            continue
        src = it["path"].read_text(encoding="utf-8", errors="replace")
        base = Counter(f["rule"] for f in analyse(rules, src, it["id"]))
        if "AG000" in base:
            continue
        for name, fn in TRANSFORMS.items():
            try:
                new = Counter(f["rule"] for f in analyse(rules, fn(src), it["id"]))
            except (SyntaxError, ValueError, RecursionError):
                stats[name]["transform_failed"] += 1
                continue
            stats[name]["files"] += 1
            if new == base:
                stats[name]["unchanged"] += 1
            else:
                diffs.append(
                    {"id": it["id"], "transform": name, "before": dict(base), "after": dict(new)}
                )
    print(f"== metamorphic {corpus}/{split} [{rev or 'working-tree'}]")
    for name, c in stats.items():
        print(
            f"  {name:18s} unchanged {fmt(c['unchanged'], c['files'])}; transform failed on {c['transform_failed']}"
        )
    out = RESULTS / f"metamorphic_{corpus}_{split}_{rev or 'working-tree'}.json"
    out.write_text(
        json.dumps(
            {"stats": {k: dict(v) for k, v in stats.items()}, "differences": diffs}, indent=1
        ),
        encoding="utf-8",
    )
    print(f"{len(diffs)} differences written to {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("score-generated", "audit", "score-audit", "metamorphic"):
        p = sub.add_parser(name)
        p.add_argument("--split", choices=["dev", "test"], required=True)
        p.add_argument("--rules", default=None)
        if name == "metamorphic":
            p.add_argument("--corpus", choices=["generated", "human"], required=True)
        if name == "audit":
            p.add_argument("--show", nargs=2, type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "score-generated":
        cmd_score_generated(a.split, a.rules)
    elif a.cmd == "audit":
        cmd_audit(a.split, a.rules, tuple(a.show) if a.show else None)  # type: ignore[arg-type]
    elif a.cmd == "score-audit":
        cmd_score_audit(a.split, a.rules)
    else:
        cmd_metamorphic(a.corpus, a.split, a.rules)


if __name__ == "__main__":
    main()
