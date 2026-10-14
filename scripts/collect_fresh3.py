"""Collect corpus F3 (docs/PROTOCOL_V4.md): real code from repositories not used in H, 20 to 500 stars.

    python scripts/collect_fresh.py

Reuses the file rules of collect_human.py. Code goes under corpus/fresh/ (git-ignored); only the manifest
corpus/manifest_fresh3.jsonl (repo, commit SHA, path, file SHA-256) is committed.
"""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import collect_human as h

ROOT = Path(__file__).resolve().parent.parent
FRESH = ROOT / "corpus" / "fresh3"
MANIFEST = ROOT / "corpus" / "manifest_fresh3.jsonl"
TOPICS = [*h.TOPICS, "spark"]
PER_TOPIC = 100
PER_STRATUM = 100
PER_REPO = 3
SEED = 4


def search(topic: str) -> list[dict[str, Any]]:
    out = subprocess.run(
        ["gh", "search", "repos", "--topic", topic, "--language", "python", "--stars", "5..500",
         "--created", ">=2024-01-01", "--sort", "updated", "--limit", str(PER_TOPIC),
         "--json", "fullName,isFork,isArchived,stargazersCount,size"],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )  # fmt: skip
    rows: list[dict[str, Any]] = json.loads(out.stdout)
    return rows


def clone(full: str) -> tuple[str, str | None]:
    dest = FRESH / full.replace("/", "__")
    if not dest.exists():
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "-q", f"https://github.com/{full}.git", str(dest)],
            capture_output=True, text=True, check=False,
        )  # fmt: skip
        if r.returncode != 0:
            return full, None
    sha = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    ).stdout.strip()
    return full, sha or None


def main() -> None:
    FRESH.mkdir(parents=True, exist_ok=True)
    used = {json.loads(x)["repo"] for x in h.MANIFEST.read_text(encoding="utf-8").splitlines()}
    # every repository cloned for H or F is excluded, not only those sampled
    for prior in ("fresh", "fresh2"):
        used |= {d.name.replace("__", "/", 1) for d in (ROOT / "corpus" / prior).iterdir() if d.is_dir()}
    repos: dict[str, dict[str, Any]] = {}
    for topic in TOPICS:
        for r in search(topic):
            name = r["fullName"]
            if (
                r["isFork"]
                or r["isArchived"]
                or name in used
                or name.split("/")[-1].lower().startswith("awesome")
                or r["size"] > 400_000
            ):
                continue
            repos.setdefault(name, r)
    print(f"usable repositories {len(repos)} (excluded {len(used)} used in H)", flush=True)
    shas: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for full, sha in pool.map(clone, sorted(repos)):
            if sha:
                shas[full] = sha
    print(f"cloned {len(shas)}", flush=True)

    pool_files: dict[str, list[tuple[str, str, int, str]]] = {"pyspark": [], "polars": [], "pandas": []}
    for full in sorted(shas):
        root = FRESH / full.replace("/", "__")
        for p in sorted(root.rglob("*.py")):
            rel = p.relative_to(root)
            if (
                any(part.lower() in h.SKIP_DIRS for part in rel.parts[:-1])
                or p.name.startswith("test_")
                or p.name == "__init__.py"
            ):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            n = text.count("\n") + 1
            if not 15 <= n <= 1500:
                continue
            s = h.stratum_of(text)
            if s:
                pool_files[s].append((full, rel.as_posix(), n, hashlib.sha256(text.encode()).hexdigest()))
    print("candidate pool:", {s: {"files": len(v), "repos": len({f for f, *_ in v})} for s, v in pool_files.items()})

    rng = random.Random(SEED)
    chosen: list[dict[str, Any]] = []
    for stratum, files in pool_files.items():
        shuffled = files[:]
        rng.shuffle(shuffled)
        taken: dict[str, int] = {}
        got = 0
        for full, rel, n, digest in shuffled:
            if got >= PER_STRATUM:
                break
            if taken.get(full, 0) >= PER_REPO:
                continue
            taken[full] = taken.get(full, 0) + 1
            got += 1
            chosen.append(
                {"stratum": stratum, "repo": full, "commit": shas[full], "path": rel, "lines": n, "sha256": digest}
            )
    MANIFEST.write_text("\n".join(json.dumps(c) for c in chosen) + "\n", encoding="utf-8")
    print(
        f"sampled {len(chosen)} files from {len({c['repo'] for c in chosen})} repositories; "
        f"by stratum { {s: sum(1 for c in chosen if c['stratum'] == s) for s in pool_files} }"
    )


if __name__ == "__main__":
    main()
