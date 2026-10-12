"""Helpers for blind labelling of the model-written corpus (they never run the analyser).

    python scripts/label_tools.py show S01 S02 S03     # print those tasks' scripts, all models, with line numbers
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "corpus" / "generated"
LABELS = ROOT / "corpus" / "labels_generated.json"
MODELS = ("qwen", "mistral", "llama", "gemma")


def load() -> dict[str, dict[str, object]]:
    return json.loads(LABELS.read_text(encoding="utf-8")) if LABELS.exists() else {}


def add(sid: str, positives: list[tuple[str, int, bool]], parses: bool = True) -> None:
    labels = load()
    labels[sid] = {
        "parses": parses,
        "positives": [{"rule": r, "line": ln, "actionable": a} for r, ln, a in positives],
    }
    LABELS.write_text(json.dumps(labels, indent=1, sort_keys=True), encoding="utf-8")


def show(task: str) -> None:
    for tag in MODELS:
        p = GEN / f"{task}__{tag}.py"
        print(f"\n===== {task}__{tag} =====")
        if not p.exists():
            print("(no script: generation produced no code block)")
            continue
        src = p.read_text(encoding="utf-8")
        try:
            ast.parse(src)
        except SyntaxError as exc:
            print(f"(does not parse: {exc.msg} at line {exc.lineno})")
        for n, line in enumerate(src.splitlines(), start=1):
            print(f"{n:3d} {line}")


if __name__ == "__main__":
    if sys.argv[1] == "show":
        for t in sys.argv[2:]:
            show(t)
