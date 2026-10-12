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
@click.option(
    "--fail-on",
    type=click.Choice(["critical", "warning", "never"]),
    default="critical",
    help="Lowest severity that makes the exit code 1.",
)
def main(paths: tuple[Path, ...], fmt: str, fail_on: str) -> None:
    """Lint PATHS (files or directories). Exit 1 if a finding at or above --fail-on exists."""
    findings: list[Finding] = []
    for f in _py_files(paths):
        findings.extend(analyze_source(f.read_text(encoding="utf-8"), str(f)))
    click.echo(to_sarif(findings) if fmt == "sarif" else to_json(findings))
    failing = {"critical": {Severity.CRITICAL}, "warning": set(Severity), "never": set()}[fail_on]
    if any(f.severity in failing for f in findings):
        raise SystemExit(1)
