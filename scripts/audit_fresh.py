"""Audit sample and labelling helpers for corpus F (docs/PROTOCOL_V2.md).

    python scripts/audit_fresh.py draw             # writes corpus/audit_fresh.json (union of v1 and v2 findings)
    python scripts/audit_fresh.py show START END   # prints sample items START..END-1 with code context
    python scripts/audit_fresh.py label FILE       # FILE: lines "index faithful actionable" (yes/no/unclear)
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RUNS = {"v1": "results/fresh_v1-after-dev.json", "v2": "results/fresh_v2-frozen.json"}
SAMPLE = ROOT / "corpus" / "audit_fresh.json"
LABELS = ROOT / "corpus" / "labels_audit_fresh.json"
CAP = {"AG001": 60, "AG002": 10_000, "AG003": 60}


def draw() -> None:
    union: dict[tuple[str, str, int], dict[str, Any]] = {}
    for ver, rel in RUNS.items():
        for f in json.loads((ROOT / rel).read_text(encoding="utf-8"))["files"]:
            for x in f["findings"]:
                if x["rule"] == "AG000":
                    continue
                key = (x["rule"], f["id"], x["line"])
                e = union.setdefault(
                    key,
                    {"rule": x["rule"], "file": f["id"], "line": x["line"], "end_line": x["end_line"],
                     "stratum": f["framework"], "versions": []},
                )  # fmt: skip
                e["versions"].append(ver)
    rng = random.Random(1)
    out: list[dict[str, Any]] = []
    for rule in ("AG001", "AG002", "AG003"):
        items = sorted((v for k, v in union.items() if k[0] == rule), key=lambda e: (e["file"], e["line"]))
        rng.shuffle(items)
        out.extend(items[: CAP[rule]])
    for i, e in enumerate(out):
        e["index"] = i
    SAMPLE.write_text(json.dumps(out, indent=1), encoding="utf-8")
    from collections import Counter

    print(Counter(e["rule"] for e in out), "of", Counter(k[0] for k in union))


def show(a: int, b: int) -> None:
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    for e in sample[a:b]:
        repo, path = e["file"].split(":", 1)
        src = (ROOT / "corpus" / "fresh" / repo.replace("/", "__") / path).read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
        lo, hi = max(0, e["line"] - 8), min(len(src), e["end_line"] + 4)
        print(f"\n#### [{e['index']}] {e['rule']} {e['file']}:{e['line']} ({e['stratum']})")
        for n in range(lo, hi):
            mark = ">>" if e["line"] - 1 <= n <= e["end_line"] - 1 else "  "
            print(f"{mark}{n + 1:5d} {src[n][:160]}")


def label(path: str) -> None:
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    labels: dict[str, Any] = json.loads(LABELS.read_text(encoding="utf-8")) if LABELS.exists() else {}
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        i, fa, ac = ln.split()
        e = sample[int(i)]
        labels[f"{e['rule']}|{e['file']}|{e['line']}"] = {"faithful": fa, "actionable": ac}
    LABELS.write_text(json.dumps(labels, indent=1), encoding="utf-8")
    print(len(labels), "labels")


if __name__ == "__main__":
    {"draw": lambda: draw(), "show": lambda: show(int(sys.argv[2]), int(sys.argv[3])), "label": lambda: label(sys.argv[2])}[sys.argv[1]]()
