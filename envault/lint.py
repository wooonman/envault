"""Lint .env files for common issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class LintIssue:
    line_no: int
    key: str | None
    severity: str  # 'error' | 'warning'
    message: str

    def __str__(self) -> str:
        loc = f"line {self.line_no}" if self.line_no else "?"
        key_part = f" [{self.key}]" if self.key else ""
        return f"{self.severity.upper()} {loc}{key_part}: {self.message}"


def lint_lines(lines: List[str]) -> List[LintIssue]:
    """Analyse raw .env lines and return a list of LintIssues."""
    issues: List[LintIssue] = []
    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        # skip blanks and comments
        if not line.strip() or line.strip().startswith("#"):
            continue

        if "=" not in line:
            issues.append(LintIssue(lineno, None, "error", "missing '=' separator"))
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            issues.append(LintIssue(lineno, None, "error", "empty key"))
            continue

        if " " in key:
            issues.append(LintIssue(lineno, key, "error", "key contains whitespace"))

        if key != key.upper():
            issues.append(LintIssue(lineno, key, "warning", "key is not UPPER_CASE"))

        if key in seen_keys:
            issues.append(
                LintIssue(
                    lineno,
                    key,
                    "warning",
                    f"duplicate key (first seen on line {seen_keys[key]})",
                )
            )
        else:
            seen_keys[key] = lineno

        if not value:
            issues.append(LintIssue(lineno, key, "warning", "value is empty"))

        # unbalanced quotes
        for quote in ('"', "'"):
            if value.startswith(quote) and not value.endswith(quote):
                issues.append(
                    LintIssue(lineno, key, "error", f"unbalanced {quote} in value")
                )

    return issues


def lint_file(path: str) -> List[LintIssue]:
    """Convenience wrapper that reads a file and lints it."""
    with open(path, "r", encoding="utf-8") as fh:
        return lint_lines(fh.readlines())


def format_lint_report(issues: List[LintIssue]) -> str:
    if not issues:
        return "No issues found."
    return "\n".join(str(i) for i in issues)
