"""Score corpus F3 (docs/PROTOCOL_V4.md). v3 and v4 report identical AG003 findings on F3, so one table covers both.

    python scripts/score_fresh3.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from evaluate import wilson

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    sample = json.loads((ROOT / "corpus" / "audit_fresh3.json").read_text(encoding="utf-8"))
    labels = json.loads((ROOT / "corpus" / "labels_audit_fresh3.json").read_text(encoding="utf-8"))
    only_one_version = [e for e in sample if len(e["versions"]) < 2]
    out: dict[str, object] = {"findings_reported_by_only_one_version": len(only_one_version)}
    for rule in ("AG003", "AG002"):
        items = [e for e in sample if e["rule"] == rule]
        lab = [labels[f"{e['rule']}|{e['file']}|{e['line']}"] for e in items]
        fk = sum(1 for x in lab if x["faithful"] == "yes")
        ak = sum(1 for x in lab if x["actionable"] == "yes")
        n = len(items)
        repos = len({e["file"].split(":")[0] for e in items})
        act_repos = len({e["file"].split(":")[0] for e, x in zip(items, lab, strict=True) if x["actionable"] == "yes"})
        fl, fh = wilson(fk, n)
        al, ah = wilson(ak, n)
        out[rule] = {"n": n, "faithful": [fk, n, fl, fh], "actionable": [ak, n, al, ah], "repos": repos, "actionable_repos": act_repos}
        print(f"{rule}: audited {n} from {repos} repos | rule-faithful {fk}/{n} = {fk / n:.3f} [{fl:.3f}, {fh:.3f}] | actionable {ak}/{n} = {ak / n:.3f} [{al:.3f}, {ah:.3f}] from {act_repos} repos")
    top = Counter(e["file"].split(":")[0] for e in sample if e["rule"] == "AG003").most_common(3)
    print("largest repositories:", top)
    out["largest_repositories"] = top
    (ROOT / "results" / "fresh3_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
