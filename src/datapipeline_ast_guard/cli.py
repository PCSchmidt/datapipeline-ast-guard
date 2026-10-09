from __future__ import annotations

from pathlib import Path

import click

from .report import to_json, to_sarif
from .rules import Finding, Severity, analyze_source


def _py_files(paths: tuple[Path, ...]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        files.extend(sorted(p.rglob("*.py")) if p.is_dir() else [p])
    return files


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--format", "fmt", type=click.Choice(["json", "sarif"]), default="json")
def main(paths: tuple[Path, ...], fmt: str) -> None:
    """Lint PATHS (files or directories). Exit 1 if any critical finding exists."""
    findings: list[Finding] = []
    for f in _py_files(paths):
        findings.extend(analyze_source(f.read_text(encoding="utf-8"), str(f)))
    click.echo(to_sarif(findings) if fmt == "sarif" else to_json(findings))
    if any(f.severity is Severity.CRITICAL for f in findings):
        raise SystemExit(1)
