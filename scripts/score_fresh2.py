"""Score corpus F2 (docs/PROTOCOL_V3.md): AG003 and AG002 precision per version, with the stratified weighting.

    python scripts/score_fresh2.py

The audit labelled every finding that only one version reports, and a random 60 of the findings both report; the
common findings are therefore weighted by (number of common findings) / (number labelled) when estimating a
version's precision over all its findings.
"""

from __future__ import annotations

import json
from pathlib import Path

from evaluate import wilson

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    sample = json.loads((ROOT / "corpus" / "audit_fresh2.json").read_text(encoding="utf-8"))
    labels = json.loads((ROOT / "corpus" / "labels_audit_fresh2.json").read_text(encoding="utf-8"))
    runs = {v: json.loads((ROOT / f"results/fresh2_{r}.json").read_text(encoding="utf-8")) for v, r in (("v2", "v2-frozen"), ("v3", "v3-frozen"))}
    out: dict[str, object] = {}
    for rule in ("AG003", "AG002"):
        items = [e for e in sample if e["rule"] == rule]
        common = [e for e in items if len(e["versions"]) == 2]
        union_common_n = len(
            {
                (f["id"], x["line"])
                for f in runs["v2"]["files"]
                for x in f["findings"]
                if x["rule"] == rule
            }
            & {
                (f["id"], x["line"])
                for f in runs["v3"]["files"]
                for x in f["findings"]
                if x["rule"] == rule
            }
        )
        w = union_common_n / len(common) if common else 1.0
        for ver in ("v2", "v3"):
            mine = [e for e in items if ver in e["versions"]]
            for key in ("faithful", "actionable"):
                tot = 0.0
                hit = 0.0
                for e in mine:
                    lab = labels[f"{e['rule']}|{e['file']}|{e['line']}"][key]
                    wt = w if len(e["versions"]) == 2 else 1.0
                    if key == "faithful" and lab == "unclear":
                        continue
                    tot += wt
                    hit += wt if lab == "yes" else 0.0
                # unweighted Wilson on the labelled instances, weighted point estimate beside it
                k = sum(1 for e in mine if labels[f"{e['rule']}|{e['file']}|{e['line']}"][key] == "yes")
                n = sum(1 for e in mine if labels[f"{e['rule']}|{e['file']}|{e['line']}"][key] != "unclear")
                lo, hi = wilson(k, n)
                print(f"{rule} {ver} {key:10s}: labelled {k}/{n} = {k / n:.3f} [{lo:.3f}, {hi:.3f}] | weighted over all {tot:.0f} findings = {hit / tot:.3f}")
                out[f"{rule}_{ver}_{key}"] = {"k": k, "n": n, "wilson": [lo, hi], "weighted": hit / tot, "weighted_n": tot}
    (ROOT / "results" / "fresh2_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
