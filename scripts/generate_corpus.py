"""Generate the model-written corpus G (docs/PROTOCOL.md): one script per (task, model) from a local Ollama server.

    python scripts/generate_corpus.py            # resumable: existing scripts are skipped

Scripts go to corpus/generated/<task>__<tag>.py (only the Apache-2.0 models' scripts are committed; see
.gitignore). A manifest line per attempt goes to corpus/manifest_generated.jsonl.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "corpus" / "tasks.json"
OUT = ROOT / "corpus" / "generated"
MANIFEST = ROOT / "corpus" / "manifest_generated.jsonl"
URL = "http://localhost:11434/api/chat"
MODELS = {
    "qwen": "qwen2.5-coder:7b-instruct-q4_K_M",
    "mistral": "mistral:7b-instruct-v0.3-q4_K_M",
    "llama": "llama3.2:3b-instruct-q8_0",
    "gemma": "gemma4:12b",
}
SYSTEM = "You are a data engineer. Reply with one complete Python script in a single code block."
FENCE = re.compile(r"```(?:python|py)?[ \t]*\r?\n(.*?)```", re.DOTALL | re.IGNORECASE)


def seed_of(task_id: str, tag: str) -> int:
    return int(hashlib.sha256(f"{task_id}|{tag}".encode()).hexdigest()[:8], 16)


def chat(model: str, task: str, seed: int, tag: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "stream": False,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": task}],
        "options": {"temperature": 0.7, "seed": seed, "num_predict": 1800},
    }
    if tag == "gemma":
        body["think"] = False
    last: Exception | None = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=900) as resp:
                out: dict[str, Any] = json.loads(resp.read())
                return out
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last = exc
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"ollama request failed: {last}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    done = set()
    if MANIFEST.exists():
        done = {
            (r["task"], r["model_tag"])
            for r in (json.loads(x) for x in MANIFEST.read_text(encoding="utf-8").splitlines() if x)
        }
    t0 = time.perf_counter()
    with MANIFEST.open("a", encoding="utf-8") as mf:
        for tag, model in MODELS.items():
            for t in tasks:
                if (t["id"], tag) in done:
                    continue
                seed = seed_of(t["id"], tag)
                started = time.perf_counter()
                res = chat(model, t["task"], seed, tag)
                text = res.get("message", {}).get("content", "") or ""
                m = FENCE.search(text)
                code = m.group(1) if m else ""
                path = OUT / f"{t['id']}__{tag}.py"
                if code.strip():
                    path.write_text(code, encoding="utf-8")
                rec = {
                    "task": t["id"], "framework": t["framework"], "model_tag": tag, "model": model, "seed": seed,
                    "ok": bool(code.strip()), "sha256": hashlib.sha256(code.encode()).hexdigest() if code.strip() else None,
                    "eval_count": res.get("eval_count"), "seconds": round(time.perf_counter() - started, 1),
                }  # fmt: skip
                mf.write(json.dumps(rec) + "\n")
                mf.flush()
                print(
                    f"{t['id']} {tag}: ok={rec['ok']} {rec['seconds']}s  (elapsed {time.perf_counter() - t0:.0f}s)",
                    flush=True,
                )


if __name__ == "__main__":
    main()
