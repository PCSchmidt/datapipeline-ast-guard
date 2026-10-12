"""Collect corpus H (docs/PROTOCOL.md): real human-written pipeline code from public GitHub repositories.

    python scripts/collect_human.py

Repositories come from `gh search repos` (topics below, language Python, by stars, no forks or archived
repos). Each is shallow-cloned under corpus/human/ (git-ignored: the code is never committed), a seeded
stratified sample of files is drawn, and a manifest of repo, commit SHA, path and file SHA-256 is written to
corpus/manifest_human.jsonl.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HUMAN = ROOT / "corpus" / "human"
MANIFEST = ROOT / "corpus" / "manifest_human.jsonl"
CANDIDATES = ROOT / "corpus" / "human_candidates.json"
TOPICS = ["pyspark", "polars", "etl", "data-pipeline", "data-engineering", "airflow"]
PER_TOPIC = 40
PER_STRATUM = 100
PER_REPO = 5
SEED = 0
SKIP_DIRS = {
    "test",
    "tests",
    "venv",
    ".venv",
    "site-packages",
    "node_modules",
    "migrations",
    "vendor",
    "build",
    "dist",
}
IMPORT = {
    "pyspark": re.compile(r"^\s*(?:from|import)\s+pyspark\b", re.MULTILINE),
    "polars": re.compile(r"^\s*(?:from|import)\s+polars\b", re.MULTILINE),
    "pandas": re.compile(r"^\s*(?:from|import)\s+pandas\b", re.MULTILINE),
}


def gh_search(topic: str) -> list[dict[str, Any]]:
    out = subprocess.run(
        ["gh", "search", "repos", "--topic", topic, "--language", "python", "--sort", "stars", "--limit", str(PER_TOPIC),
         "--json", "fullName,isFork,isArchived,stargazersCount,size,defaultBranch"],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )  # fmt: skip
    rows: list[dict[str, Any]] = json.loads(out.stdout)
    return rows


def clone(full: str) -> tuple[str, str | None]:
    dest = HUMAN / full.replace("/", "__")
    if not dest.exists():
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "-q", f"https://github.com/{full}.git", str(dest)],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode != 0:
            return full, None
    sha = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    ).stdout.strip()
    return full, sha or None


def stratum_of(text: str) -> str | None:
    if IMPORT["pyspark"].search(text):
        return "pyspark"
    if IMPORT["polars"].search(text):
        return "polars"
    if IMPORT["pandas"].search(text):
        return "pandas"
    return None


def split_of(full: str) -> str:
    return "dev" if hashlib.sha256(full.encode()).digest()[0] % 2 == 0 else "test"


def main() -> None:
    HUMAN.mkdir(parents=True, exist_ok=True)
    repos: dict[str, dict[str, Any]] = {}
    per_topic: dict[str, int] = {}
    for topic in TOPICS:
        found = gh_search(topic)
        per_topic[topic] = len(found)
        for r in found:
            if (
                r["isFork"]
                or r["isArchived"]
                or r["fullName"].split("/")[-1].lower().startswith("awesome")
            ):
                continue
            if r["size"] > 400_000:  # KB; skip very large repositories
                continue
            repos.setdefault(r["fullName"], r)
    print(f"topic hits {per_topic}; usable repositories {len(repos)}", flush=True)
    shas: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for full, sha in pool.map(clone, sorted(repos)):
            if sha:
                shas[full] = sha
    print(f"cloned {len(shas)} repositories", flush=True)

    pool_files: dict[str, list[tuple[str, str, int, str]]] = {
        "pyspark": [],
        "polars": [],
        "pandas": [],
    }
    for full, sha in sorted(shas.items()):
        root = HUMAN / full.replace("/", "__")
        for p in sorted(root.rglob("*.py")):
            rel = p.relative_to(root)
            if (
                any(part.lower() in SKIP_DIRS for part in rel.parts[:-1])
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
            s = stratum_of(text)
            if s:
                pool_files[s].append(
                    (full, rel.as_posix(), n, hashlib.sha256(text.encode()).hexdigest())
                )
    counts = {s: {"files": len(v), "repos": len({f for f, *_ in v})} for s, v in pool_files.items()}
    print("candidate pool:", counts, flush=True)

    rng = random.Random(SEED)
    chosen: list[dict[str, Any]] = []
    for stratum, files in pool_files.items():
        shuffled = files[:]
        rng.shuffle(shuffled)
        taken: dict[str, int] = {}
        for full, rel, n, digest in shuffled:
            if len([c for c in chosen if c["stratum"] == stratum]) >= PER_STRATUM:
                break
            if taken.get(full, 0) >= PER_REPO:
                continue
            taken[full] = taken.get(full, 0) + 1
            chosen.append(
                {
                    "stratum": stratum,
                    "repo": full,
                    "commit": shas[full],
                    "path": rel,
                    "lines": n,
                    "sha256": digest,
                    "split": split_of(full),
                }
            )
    MANIFEST.write_text("\n".join(json.dumps(c) for c in chosen) + "\n", encoding="utf-8")
    CANDIDATES.write_text(
        json.dumps({"topics": per_topic, "repos_cloned": len(shas), "pool": counts}, indent=1),
        encoding="utf-8",
    )
    by = {
        (s, sp): sum(1 for c in chosen if c["stratum"] == s and c["split"] == sp)
        for s in pool_files
        for sp in ("dev", "test")
    }
    print(
        f"sampled {len(chosen)} files from {len({c['repo'] for c in chosen})} repositories; by stratum and split {by}"
    )


if __name__ == "__main__":
    main()
