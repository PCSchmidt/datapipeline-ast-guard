"""Flagged-file rate and findings per 1,000 lines on the human corpus H, with repository-level bootstrap intervals.

    python scripts/summarise_human.py            # reads results/human_{dev,test}_*.json written by evaluate.py run

Files within a repository are not independent, so the bootstrap resamples repositories (docs/PROTOCOL.md).
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
RUNS = {
    "v0-as-shipped": {"dev": "human_dev_v0.json", "test": "human_test_v0-as-shipped.json"},
    "v1-after-dev": {"dev": "human_dev_v1.json", "test": "human_test_v1-after-dev.json"},
}
RULES = ("AG001", "AG002", "AG003")


def load(rev: str, split: str) -> list[dict[str, Any]]:
    return list(json.loads((RESULTS / RUNS[rev][split]).read_text(encoding="utf-8"))["files"])


def stats(files: list[dict[str, Any]]) -> dict[str, float]:
    n = len(files)
    lines = sum(f["lines"] for f in files)
    flagged = sum(1 for f in files if f["findings"])
    out: dict[str, float] = {"files": n, "lines": lines, "flagged_rate": flagged / n if n else 0.0}
    total = 0
    for r in RULES:
        c = sum(1 for f in files for x in f["findings"] if x["rule"] == r)
        out[r] = c
        total += c
    out["per_kloc"] = 1000 * total / lines if lines else 0.0
    return out


def boot(files: list[dict[str, Any]], b: int = 2000) -> dict[str, list[float]]:
    by_repo: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for f in files:
        by_repo[f["repo"]].append(f)
    repos = sorted(by_repo)
    rng = random.Random(0)
    rates, dens = [], []
    for _ in range(b):
        sample = [f for r in (rng.choice(repos) for _ in repos) for f in by_repo[r]]
        s = stats(sample)
        rates.append(s["flagged_rate"])
        dens.append(s["per_kloc"])
    rates.sort()
    dens.sort()
    pick = lambda xs, q: xs[int(q * (len(xs) - 1))]
    return {
        "flagged_rate_ci95": [pick(rates, 0.025), pick(rates, 0.975)],
        "per_kloc_ci95": [pick(dens, 0.025), pick(dens, 0.975)],
    }


def main() -> None:
    result: dict[str, Any] = {}
    for rev in RUNS:
        files = load(rev, "dev") + load(rev, "test")
        result[rev] = {"all": {**stats(files), **boot(files)}}
        for stratum in ("pyspark", "polars", "pandas"):
            sub = [f for f in files if f["framework"] == stratum]
            result[rev][stratum] = {**stats(sub), **boot(sub)}
        print(
            f"== {rev} (dev + test, {int(result[rev]['all']['files'])} files, {int(result[rev]['all']['lines'])} lines)"
        )
        for key, s in result[rev].items():
            lo, hi = s["flagged_rate_ci95"]
            kl, kh = s["per_kloc_ci95"]
            print(
                f"  {key:8s} flagged {s['flagged_rate']:.3f} [{lo:.3f}, {hi:.3f}] | findings/KLOC {s['per_kloc']:.2f} [{kl:.2f}, {kh:.2f}] | AG001 {int(s['AG001'])} AG002 {int(s['AG002'])} AG003 {int(s['AG003'])}"
            )
    (RESULTS / "human_summary.json").write_text(json.dumps(result, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
