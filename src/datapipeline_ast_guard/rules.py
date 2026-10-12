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
_BOUNDERS = {"limit", "head", "take", "first", "sample", "fetch", "slice"}
# Modules whose `collect` is not a dataset materialisation (`gc.collect()`, `F.collect(...)` on the functions alias).
_NON_DATASET_RECEIVERS = {"gc", "F", "functions"}
# Keyword names that give a join its keys or condition (PySpark/pandas/Polars/PyArrow/DuckDB/Ibis spellings).
_KEY_KWARGS = (
    "on",
    "left_on",
    "right_on",
    "using",
    "keys",
    "right_keys",
    "condition",
    "predicates",
)
_ARGUMENT_FREE_BUILTINS = {
    "map",
    "sorted",
    "reversed",
    "filter",
    "list",
    "set",
    "tuple",
    "range",
    "enumerate",
    "zip",
    "iter",
}
_PATH = re.compile(
    r"^(?:[A-Za-z]:[\\/]|/(?:[\w.\-]+/)+[\w.\-]*|(?:s3a?|gs|abfss?|hdfs|dbfs|file):/{1,3})"
)
_IGNORE = re.compile(r"#\s*ast-guard:\s*ignore\[([A-Z0-9, ]+)\]")
_STRING_TEST_METHODS = {"startswith", "endswith", "removeprefix", "removesuffix"}


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


def _root_name(expr: ast.expr) -> str | None:
    """The variable at the start of `name.a().b()[0]`, if the chain starts at a plain name."""
    node: ast.expr = expr
    while True:
        if isinstance(node, ast.Attribute):
            node = node.value
        elif isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Subscript):
            node = node.value
        elif isinstance(node, ast.Name):
            return node.id
        else:
            return None


def _kw(call: ast.Call, name: str) -> ast.expr | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


_NOT_A_DATAFRAME_ARG = (ast.List, ast.Tuple, ast.Set, ast.ListComp, ast.SetComp, ast.GeneratorExp)


def _looks_like_string_or_path_join(call: ast.Call) -> bool:
    """`", ".join(xs)`, `f"..".join(xs)`, `os.path.join(a)`, `sep.join([...])` are not DataFrame joins."""
    assert isinstance(call.func, ast.Attribute)
    recv = call.func.value
    if isinstance(recv, (ast.Constant, ast.JoinedStr)):
        return True
    if isinstance(recv, ast.Attribute) and recv.attr == "path":  # os.path / posixpath-style
        return True
    if not call.args:
        return False
    first = call.args[0]
    if isinstance(first, _NOT_A_DATAFRAME_ARG):
        return True
    return (
        isinstance(first, ast.Call)
        and isinstance(first.func, ast.Name)
        and first.func.id in _ARGUMENT_FREE_BUILTINS
    )  # `sep.join(map(str, xs))`


def _is_cross_or_keyless_join(call: ast.Call) -> bool:
    if _looks_like_string_or_path_join(call):
        return False
    how = _kw(call, "how")
    if isinstance(how, ast.Constant) and how.value == "cross":
        return True
    if any(_kw(call, k) is not None for k in _KEY_KWARGS):
        return False
    # A DataFrame join takes the other frame: `thread.join()` / `queue.join()` / `proc.join(timeout=5)` do not.
    if not call.args and _kw(call, "other") is None and _kw(call, "right") is None:
        return False
    # PySpark join(other, on, how) / Polars join(other, on): a second positional arg names keys.
    return len(call.args) < 2


class _Visitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.findings: list[Finding] = []
        # Names assigned from a bounded frame (`small = df.limit(5)`), one set per scope, so that a later
        # `small.collect()` is recognised as bounded.
        self._bounded: list[set[str]] = [set()]

    def _add(self, rule: str, node: ast.AST) -> None:
        sev, msg = RULES[rule]
        line = getattr(node, "lineno", 1)
        col = getattr(node, "col_offset", 0)
        self.findings.append(Finding(rule, sev, msg, self.path, line, col))

    # -- scopes and bounded names ---------------------------------------------------------------------

    def _scoped(self, node: ast.AST) -> None:
        self._bounded.append(set())
        self.generic_visit(node)
        self._bounded.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # Decorator arguments are routes and registrations (`@router.get("/items")`), never data paths, so
        # decorators are not visited. Argument defaults belong to the enclosing scope; the body gets its own.
        self.visit(node.args)
        self._bounded.append(set())
        for stmt in node.body:
            self.visit(stmt)
        self._bounded.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scoped(node)

    def _bounds(self, expr: ast.expr) -> bool:
        if isinstance(expr, ast.Call):
            if _chain_attrs(expr) & _BOUNDERS:
                return True
            root = _root_name(expr)
            return root is not None and root in self._bounded[-1]
        if isinstance(expr, ast.Name):
            return expr.id in self._bounded[-1]
        return False

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        bounded = self._bounds(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                (self._bounded[-1].add if bounded else self._bounded[-1].discard)(target.id)
            else:
                self.visit(target)

    # -- rules ----------------------------------------------------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr in _MATERIALISERS and not self._bounds(node) and not self._is_non_dataset(node):
                self._add("AG001", node)
            if attr == "crossJoin" or (attr == "join" and _is_cross_or_keyless_join(node)):
                self._add("AG002", node)
            if (
                attr in _STRING_TEST_METHODS
            ):  # `uri.startswith("file://")` tests a scheme, it names no path
                self.visit(node.func)
                for arg in node.args:
                    if not isinstance(arg, ast.Constant):
                        self.visit(arg)
                for kw in node.keywords:
                    self.visit(kw)
                return
        self.generic_visit(node)

    @staticmethod
    def _is_non_dataset(node: ast.Call) -> bool:
        assert isinstance(node.func, ast.Attribute)
        recv = node.func.value
        return isinstance(recv, ast.Name) and recv.id in _NON_DATASET_RECEIVERS

    def visit_keyword(self, node: ast.keyword) -> None:
        if node.arg == "prefix" and isinstance(node.value, ast.Constant):
            return  # `APIRouter(prefix="/api/items")`: a URL prefix
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        # Only an f-string that BEGINS with the path is a hard-coded path; `f"{base}/part/"` is a fragment.
        for i, part in enumerate(node.values):
            if isinstance(part, ast.Constant):
                if i == 0:
                    self.visit_Constant(part)
            else:
                self.visit(part)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self.visit(node.left)
        right_is_fragment = (
            isinstance(node.op, ast.Add)
            and isinstance(node.right, ast.Constant)
            and not isinstance(node.left, ast.Constant)
        )
        if (
            not right_is_fragment
        ):  # `config_dir + "/sales/"` appends a fragment to a configured base
            self.visit(node.right)

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
