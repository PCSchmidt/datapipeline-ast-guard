from __future__ import annotations

import json
from typing import Any

from .rules import RULES, Finding, Severity

_LEVEL = {Severity.CRITICAL: "error", Severity.WARNING: "warning"}


def to_json(findings: list[Finding]) -> str:
    return json.dumps(
        [
            {
                "rule": f.rule_id,
                "severity": f.severity.value,
                "message": f.message,
                "path": f.path,
                "line": f.line,
                "col": f.col,
            }
            for f in findings
        ],
        indent=2,
    )


def to_sarif(findings: list[Finding]) -> str:
    rules: list[dict[str, Any]] = [
        {
            "id": rid,
            "shortDescription": {"text": msg},
            "defaultConfiguration": {"level": _LEVEL[sev]},
        }
        for rid, (sev, msg) in RULES.items()
    ]
    results = [
        {
            "ruleId": f.rule_id,
            "level": _LEVEL[f.severity],
            "message": {"text": f.message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": f.path.replace("\\", "/")},
                        "region": {"startLine": f.line, "startColumn": f.col + 1},
                    }
                }
            ],
        }
        for f in findings
    ]
    doc = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {"driver": {"name": "datapipeline-ast-guard", "rules": rules}},
                "results": results,
            }
        ],
    }
    return json.dumps(doc, indent=2)
