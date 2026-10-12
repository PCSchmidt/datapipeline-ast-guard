"""Score corpus F (docs/PROTOCOL_V2.md): audited precision per rule and version, flagged-file rate, gate failures.

    python scripts/score_fresh.py
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from evaluate import load_rules, wilson

ROOT = Path(__file__).resolve().parent.parent
REVS = {"v1": "v1-after-dev", "v2": "v2-frozen"}


def ci(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} [{lo:.3f}, {hi:.3f}]" if n else "0/0"


def boot(files: list[dict[str, Any]], pick: Any, b: int = 2000) -> tuple[float, float, float]:
    by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for f in files:
        by[f["repo"]].append(f)
    repos = sorted(by)
    rng = random.Random(0)
    vals = []
    for _ in range(b):
        s = [f for r in (rng.choice(repos) for _ in repos) for f in by[r]]
        vals.append(sum(1 for f in s if pick(f)) / len(s))
    vals.sort()
    pt = sum(1 for f in files if pick(f)) / len(files)
    return pt, vals[int(0.025 * (b - 1))], vals[int(0.975 * (b - 1))]


def main() -> None:
    sample = json.loads((ROOT / "corpus" / "audit_fresh.json").read_text(encoding="utf-8"))
    labels = json.loads((ROOT / "corpus" / "labels_audit_fresh.json").read_text(encoding="utf-8"))
    out: dict[str, Any] = {"audit": {}, "files": {}}
    for ver in REVS:
        print(f"== {ver} audited findings")
        out["audit"][ver] = {}
        for rule in ("AG001", "AG002", "AG003"):
            items = [e for e in sample if e["rule"] == rule and ver in e["versions"]]
            lab = [labels[f"{e['rule']}|{e['file']}|{e['line']}"] for e in items]
            fy = sum(1 for x in lab if x["faithful"] == "yes")
            fn = sum(1 for x in lab if x["faithful"] == "no")
            ay = sum(1 for x in lab if x["actionable"] == "yes")
            out["audit"][ver][rule] = {"n": len(items), "faithful": [fy, fy + fn], "actionable": [ay, len(items)]}
            print(f"  {rule}: audited {len(items)} | rule-faithful {ci(fy, fy + fn)} | actionable {ci(ay, len(items))}")
    # file-level rates and gate failures (severity recomputed from the frozen rules)
    from evaluate import corpus_files

    items = corpus_files("fresh", "all")
    for ver, rev in REVS.items():
        rules = load_rules(rev)
        recs = []
        for it in items:
            src = it["path"].read_text(encoding="utf-8", errors="replace")
            fs = rules.analyze_source(src, it["id"])
            recs.append(
                {
                    "repo": it["repo"],
                    "framework": it["framework"],
                    "flagged": bool(fs),
                    "flagged_excl_ag000": any(f.rule_id != "AG000" for f in fs),
                    "fails": any(f.severity.value == "critical" for f in fs),
                    "fails_excl_ag000": any(f.severity.value == "critical" and f.rule_id != "AG000" for f in fs),
                    "rules": Counter(f.rule_id for f in fs),
                }
            )
        for name in ("flagged", "flagged_excl_ag000", "fails", "fails_excl_ag000"):
            pt, lo, hi = boot(recs, lambda r, n=name: r[n])
            out["files"][f"{ver}_{name}"] = [pt, lo, hi]
            print(f"{ver} files {name}: {pt:.3f} [{lo:.3f}, {hi:.3f}]  ({sum(1 for r in recs if r[name])}/{len(recs)})")
        tot: Counter[str] = Counter()
        for r in recs:
            tot.update(r["rules"])
        print(f"{ver} findings by rule: {dict(tot)}")
    (ROOT / "results" / "fresh_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
