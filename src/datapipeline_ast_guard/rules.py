"""AST rules. The analysed code is parsed, never imported or executed."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    message: str
    path: str
    line: int
    col: int


RULES: dict[str, tuple[Severity, str]] = {
    "AG000": (Severity.CRITICAL, "File does not parse"),
    "AG001": (Severity.CRITICAL, "Unbounded collect()/toPandas() with no preceding limit()/head()"),
    "AG002": (Severity.CRITICAL, "Cross join, or join without explicit equality keys"),
    "AG003": (Severity.WARNING, "Hard-coded file-system path"),
}

_MATERIALISERS = {"collect", "toPandas", "to_pandas"}
_BOUNDERS = {"limit", "head", "take", "first", "sample", "fetch"}
_PATH = re.compile(
    r"^(?:[A-Za-z]:[\\/]|/(?:[\w.\-]+/)+[\w.\-]*|(?:s3a?|gs|abfss?|hdfs|dbfs|file):/{1,3})"
)
_IGNORE = re.compile(r"#\s*ast-guard:\s*ignore\[([A-Z0-9, ]+)\]")


def _chain_attrs(call: ast.Call) -> set[str]:
    """Method names along `df.a().b().c()` below (and excluding) the outermost call."""
    names: set[str] = set()
    node: ast.expr = call.func
    while True:
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
            node = node.value
        elif isinstance(node, ast.Call):
            node = node.func
        else:
            return names


def _kw(call: ast.Call, name: str) -> ast.expr | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _is_cross_or_keyless_join(call: ast.Call) -> bool:
    how = _kw(call, "how")
    if isinstance(how, ast.Constant) and how.value == "cross":
        return True
    if any(_kw(call, k) is not None for k in ("on", "left_on", "using")):
        return False
    # PySpark join(other, on, how) / Polars join(other, on): a second positional arg names keys.
    return len(call.args) < 2


class _Visitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.findings: list[Finding] = []

    def _add(self, rule: str, node: ast.AST) -> None:
        sev, msg = RULES[rule]
        line = getattr(node, "lineno", 1)
        col = getattr(node, "col_offset", 0)
        self.findings.append(Finding(rule, sev, msg, self.path, line, col))

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr in _MATERIALISERS and not (_chain_attrs(node) & _BOUNDERS):
                self._add("AG001", node)
            if attr == "crossJoin" or (attr == "join" and _is_cross_or_keyless_join(node)):
                self._add("AG002", node)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and _PATH.match(node.value):
            self._add("AG003", node)


def _suppressed(source: str) -> dict[int, set[str]]:
    out: dict[int, set[str]] = {}
    for lineno, line in enumerate(source.splitlines(), start=1):
        m = _IGNORE.search(line)
        if m:
            out[lineno] = {r.strip() for r in m.group(1).split(",")}
    return out


def analyze_source(source: str, path: str = "<string>") -> list[Finding]:
    """Findings for one module. A file that does not parse yields a single critical finding."""
    try:
        tree = ast.parse(source, filename=path)
    except (SyntaxError, ValueError) as exc:
        line = getattr(exc, "lineno", None) or 1
        return [Finding("AG000", Severity.CRITICAL, f"Cannot parse: {exc}", path, line, 0)]
    visitor = _Visitor(path)
    visitor.visit(tree)
    muted = _suppressed(source)
    kept = [f for f in visitor.findings if f.rule_id not in muted.get(f.line, set())]
    return sorted(kept, key=lambda f: (f.line, f.col, f.rule_id))
