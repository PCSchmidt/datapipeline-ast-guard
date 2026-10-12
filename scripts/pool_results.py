"""Pool the audit labels and generated-corpus results into results/summary.json (docs/PROTOCOL.md).

python scripts/pool_results.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from evaluate import wilson

ROOT = Path(__file__).resolve().parent.parent
RULES = ("AG001", "AG002", "AG003")


def audit(split: str, rev: str, labels: dict[str, Any]) -> dict[str, Counter[str]]:
    sample = json.loads((ROOT / "corpus" / f"audit_{split}_{rev}.json").read_text(encoding="utf-8"))
    out: dict[str, Counter[str]] = {r: Counter() for r in RULES}
    for s in sample:
        lab = labels[s["fid"]]
        c = out[s["rule"]]
        c["n"] += 1
        c["faithful_" + lab["faithful"]] += 1
        c["actionable_" + lab["actionable"]] += 1
    return out


def main() -> None:
    labels = json.loads((ROOT / "corpus" / "labels_audit.json").read_text(encoding="utf-8"))
    summary: dict[str, Any] = {"audit": {}, "generated": {}}
    for rev, dev_name in (("v0-as-shipped", "v0-as-shipped"), ("v1-after-dev", "working-tree")):
        pooled = {r: Counter() for r in RULES}
        per_half = {}
        for split, name in (("dev", dev_name), ("test", rev)):
            a = audit(split, name, labels)
            per_half[split] = {r: dict(a[r]) for r in RULES}
            for r in RULES:
                pooled[r].update(a[r])
        table = {}
        for r in RULES:
            c = pooled[r]
            f_yes, f_no = c["faithful_yes"], c["faithful_no"]
            a_yes, a_no = c["actionable_yes"], c["actionable_no"]
            table[r] = {
                "findings_audited": c["n"],
                "faithful": [f_yes, f_yes + f_no, *wilson(f_yes, f_yes + f_no)],
                "actionable": [a_yes, c["n"], *wilson(a_yes, c["n"])],
                "unclear": c["faithful_unclear"],
            }
        summary["audit"][rev] = {"pooled": table, "per_half": per_half}

    manifest = [
        json.loads(x)
        for x in (ROOT / "corpus" / "manifest_generated.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    gen = json.loads((ROOT / "corpus" / "labels_generated.json").read_text(encoding="utf-8"))
    by_model: dict[str, Counter[str]] = {}
    for r in manifest:
        sid = f"{r['task']}__{r['model_tag']}"
        c = by_model.setdefault(r["model_tag"], Counter())
        c["scripts"] += 1
        if not r["ok"]:
            c["no_code_block"] += 1
        elif not gen[sid]["parses"]:
            c["does_not_parse"] += 1
        else:
            c["parses"] += 1
    summary["generated"]["by_model"] = {m: dict(c) for m, c in by_model.items()}
    summary["generated"]["positives"] = dict(
        Counter(p["rule"] for v in gen.values() for p in v["positives"])
    )
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    for rev, s in summary["audit"].items():
        print("==", rev, "(dev + test pooled)")
        for r, t in s["pooled"].items():
            f, a = t["faithful"], t["actionable"]
            print(
                f"  {r}: audited {t['findings_audited']} | rule-faithful {f[0]}/{f[1]} = {f[0] / f[1] if f[1] else 0:.3f} [{f[2]:.3f}, {f[3]:.3f}] | actionable {a[0]}/{a[1]} = {a[0] / a[1]:.3f} [{a[2]:.3f}, {a[3]:.3f}] | unclear {t['unclear']}"
            )
    print("== generated corpus by model:", summary["generated"]["by_model"])
    print("labelled positives:", summary["generated"]["positives"])


if __name__ == "__main__":
    main()
