"""Recall by mutation on corpus F2 (docs/PROTOCOL_V3.md).

    python scripts/mutate.py

Each mutant is one F2 file with one expression replaced so that it contains a known defect. A mutant is found if the
target rule reports on the mutated line. Sites are located from the syntax tree; mutants that do not parse are dropped
and counted.
"""

from __future__ import annotations

import ast
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

from evaluate import corpus_files, load_rules, wilson

ROOT = Path(__file__).resolve().parent.parent
SEED = 3
PER_TYPE = 100
DF_LIBS = {"pyspark", "pandas", "polars", "pyarrow", "duckdb", "ibis"}
KEY_KW = {"on", "left_on", "right_on", "using", "keys", "right_keys", "condition", "predicates"}
PATHLIKE = {"os", "posixpath", "ntpath", "path", "shlex", "pathlib"}
BOUNDERS = {"limit", "head", "take", "sample", "slice"}  # "first" returns a row, not a frame
MATERIALISERS = {"collect", "toPandas", "to_pandas"}
READERS = {
    "read_csv", "read_parquet", "read_json", "read_excel", "scan_csv", "scan_parquet",
    "scan_ndjson", "read_table", "read_feather", "read_orc", "textFile",
}  # fmt: skip
SPARK_READ_METHODS = {"csv", "parquet", "json", "orc", "load"}
DUMMY_PATH = '"/mnt/data/input.dat"'
NOT_A_FRAME = (ast.List, ast.Tuple, ast.Set, ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.Constant)
BUILTIN_ITERS = {"map", "sorted", "reversed", "filter", "list", "set", "tuple", "range", "enumerate", "zip", "iter"}


def imports(tree: ast.AST) -> set[str]:
    out: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            out.add(n.module.split(".")[0])
    return out


def chain_attrs(node: ast.expr) -> list[str]:
    names: list[str] = []
    while True:
        if isinstance(node, ast.Attribute):
            names.append(node.attr)
            node = node.value
        elif isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Subscript):
            node = node.value
        else:
            return names


def root_name(node: ast.expr) -> str | None:
    while True:
        if isinstance(node, (ast.Attribute, ast.Subscript)):
            node = node.value
        elif isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Name):
            return node.id
        else:
            return None


def line_starts(src: str) -> list[int]:
    """Character offset of each line start, splitting on \\n, \\r\\n and \\r like the parser does."""
    starts = [0]
    for m in re.finditer(r"\r\n|\r|\n", src):
        starts.append(m.end())
    return starts


def span(src: str, starts: list[int], node: ast.expr) -> tuple[int, int]:
    def off(line: int, col_bytes: int) -> int:
        text = src[starts[line - 1] :]
        return starts[line - 1] + len(text.encode("utf-8")[:col_bytes].decode("utf-8", errors="ignore"))

    assert node.end_lineno is not None and node.end_col_offset is not None
    return off(node.lineno, node.col_offset), off(node.end_lineno, node.end_col_offset)


def sites(src: str, tree: ast.Module) -> dict[str, list[dict[str, Any]]]:
    libs = imports(tree)
    starts = line_starts(src)
    bounded_names = {
        t.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Assign) and any(isinstance(c, ast.Attribute) and c.attr in BOUNDERS for c in ast.walk(n.value))
        for t in n.targets
        if isinstance(t, ast.Name)
    }
    out: dict[str, list[dict[str, Any]]] = {"M-join": [], "M-cross": [], "M-collect": [], "M-path": []}
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Attribute):
            continue
        attr = n.func.attr
        recv = n.func.value
        if attr == "join" and n.args:
            first = n.args[0]
            string_like = (
                isinstance(recv, (ast.Constant, ast.JoinedStr))
                or (isinstance(recv, ast.Attribute) and recv.attr == "path")
                or (isinstance(recv, ast.Name) and recv.id in PATHLIKE)
                or isinstance(first, NOT_A_FRAME)
                or (isinstance(first, ast.Call) and isinstance(first.func, ast.Name) and first.func.id in BUILTIN_ITERS)
            )
            if not string_like:
                kws = {k.arg for k in n.keywords}
                if "pyspark" in libs and (len(n.args) >= 2 or kws & KEY_KW):
                    seg = ast.get_source_segment(src, n.func)
                    arg = ast.get_source_segment(src, first)
                    if seg and arg:
                        a, b = span(src, starts, n)
                        out["M-join"].append({"start": a, "end": b, "text": f"{seg}({arg})", "line": n.lineno})
                how = next((k for k in n.keywords if k.arg == "how"), None)
                if (
                    libs & DF_LIBS
                    and how is not None
                    and isinstance(how.value, ast.Constant)
                    and isinstance(how.value.value, str)
                    and how.value.value != "cross"
                ):
                    a, b = span(src, starts, how.value)
                    out["M-cross"].append({"start": a, "end": b, "text": '"cross"', "line": n.lineno})
        if attr in MATERIALISERS and isinstance(recv, ast.Call) and isinstance(recv.func, ast.Attribute) and recv.func.attr in BOUNDERS:
            others = set(chain_attrs(recv.func.value)) & BOUNDERS
            root = root_name(recv.func.value)
            if not others and root not in bounded_names:
                inner = ast.get_source_segment(src, recv.func.value)
                if inner:
                    a, b = span(src, starts, recv)
                    out["M-collect"].append({"start": a, "end": b, "text": inner, "line": n.lineno})
        if n.args and not isinstance(n.args[0], ast.Constant):
            is_reader = attr in READERS or (attr in SPARK_READ_METHODS and "read" in chain_attrs(recv))
            if is_reader and not isinstance(n.args[0], (ast.List, ast.Tuple, ast.Dict, ast.Starred)):
                a, b = span(src, starts, n.args[0])
                out["M-path"].append({"start": a, "end": b, "text": DUMMY_PATH, "line": n.args[0].lineno})
    return out


def main() -> None:
    import sys

    # default: the protocol's corpus F2 only; "pooled" adds H and F (exploratory, Deviation 3)
    pooled = len(sys.argv) > 1 and sys.argv[1] == "pooled"
    sources = [("fresh2", "all")] + ([("human", "dev"), ("human", "test"), ("fresh", "all")] if pooled else [])
    rules = {v: load_rules(r) for v, r in (("v2", "v2-frozen"), ("v3", "v3-frozen"))}
    rng = random.Random(SEED)
    files = []
    items = [it for c, sp in sources for it in corpus_files(c, sp)]
    for it in items:
        src = it["path"].read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except (SyntaxError, ValueError):
            continue
        files.append((it, src, sites(src, tree)))
    summary: dict[str, Any] = {"eligible_sites": {}, "mutants": {}, "dropped_unparseable": 0}
    for mtype in ("M-join", "M-cross", "M-collect", "M-path"):
        pool = [(it, src, s[mtype]) for it, src, s in files if s[mtype]]
        summary["eligible_sites"][mtype] = {"files": len(pool), "sites": sum(len(p[2]) for p in pool)}
        picked: list[tuple[dict[str, Any], str, dict[str, Any]]] = []
        order = pool[:]
        rng.shuffle(order)
        rounds: list[list[tuple[dict[str, Any], str, dict[str, Any]]]] = []
        for it, src, ss in order:
            ss = ss[:]
            rng.shuffle(ss)
            for k, site in enumerate(ss):
                while len(rounds) <= k:
                    rounds.append([])
                rounds[k].append((it, src, site))
        for r in rounds:
            picked.extend(r)
        picked = picked[:PER_TYPE]
        target = {"M-join": "AG002", "M-cross": "AG002", "M-collect": "AG001", "M-path": "AG003"}[mtype]
        res = {v: {"n": 0, "found": 0, "collateral": 0, "lost": 0} for v in rules}
        for it, src, site in picked:
            mutant = src[: site["start"]] + site["text"] + src[site["end"] :]
            try:
                ast.parse(mutant)
            except (SyntaxError, ValueError):
                summary["dropped_unparseable"] += 1
                continue
            for v, mod in rules.items():
                orig = Counter(f.rule_id for f in mod.analyze_source(src, it["id"]))
                new_f = mod.analyze_source(mutant, it["id"])
                new = Counter(f.rule_id for f in new_f)
                found = any(f.rule_id == target and f.line == site["line"] for f in new_f)
                delta = sum(new.values()) - sum(orig.values())
                res[v]["n"] += 1
                res[v]["found"] += int(found)
                res[v]["collateral"] += int(delta - int(found) > 0)
                res[v]["lost"] += int(delta - int(found) < 0)
        summary["mutants"][mtype] = res
    (ROOT / "results" / ("mutation_pooled.json" if pooled else "mutation_f2.json")).write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary["eligible_sites"]), "dropped", summary["dropped_unparseable"])
    for mtype, res in summary["mutants"].items():
        for v, r in res.items():
            lo, hi = wilson(r["found"], r["n"])
            print(f"{mtype:10s} {v}: found {r['found']}/{r['n']} = {r['found'] / r['n'] if r['n'] else 0:.3f} [{lo:.3f}, {hi:.3f}] | extra findings in {r['collateral']} | lost findings in {r['lost']}")


if __name__ == "__main__":
    main()
