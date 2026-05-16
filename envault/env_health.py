"""Vault health check: aggregates issues across multiple dimensions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envault.vault import load_vault
from envault.pin import get_pins
from envault.ttl import get_ttl_data
from envault.env_placeholder import check_placeholders
from envault.env_lock_status import check_lock_status


@dataclass
class HealthIssue:
    severity: str  # "error" | "warning" | "info"
    category: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.category}: {self.message}"


@dataclass
class HealthReport:
    vault_path: str
    issues: List[HealthIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def __str__(self) -> str:
        return format_health_report(self)


def run_health_check(vault_path: str, password: str) -> HealthReport:
    report = HealthReport(vault_path=vault_path)
    path = Path(vault_path)

    if not path.exists():
        report.issues.append(HealthIssue("error", "vault", "Vault file does not exist"))
        return report

    # Lock status — are all entries encrypted?
    try:
        status = check_lock_status(vault_path)
        if status.unencrypted_count > 0:
            report.issues.append(HealthIssue(
                "error", "encryption",
                f"{status.unencrypted_count} entry/entries appear unencrypted"
            ))
    except Exception as exc:
        report.issues.append(HealthIssue("error", "encryption", str(exc)))

    # Placeholder detection
    try:
        ph = check_placeholders(vault_path, password)
        if ph.found:
            report.issues.append(HealthIssue(
                "warning", "placeholders",
                f"{len(ph.entries)} key(s) still contain placeholder values"
            ))
    except Exception as exc:
        report.issues.append(HealthIssue("warning", "placeholders", str(exc)))

    # Expired TTL keys
    try:
        vault = load_vault(vault_path)
        ttl_data = get_ttl_data(vault_path)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        expired = [
            k for k, v in ttl_data.items()
            if datetime.fromisoformat(v["expires_at"]) < now
        ]
        if expired:
            report.issues.append(HealthIssue(
                "warning", "ttl",
                f"{len(expired)} key(s) have expired TTL: {', '.join(expired)}"
            ))
    except Exception:
        pass

    # Empty vault warning
    try:
        vault = load_vault(vault_path)
        entries = {k: v for k, v in vault.items() if not k.startswith("__")}
        if not entries:
            report.issues.append(HealthIssue("info", "vault", "Vault is empty"))
    except Exception:
        pass

    return report


def format_health_report(report: HealthReport) -> str:
    lines = [f"Health report for: {report.vault_path}"]
    if not report.issues:
        lines.append("  All checks passed. Vault looks healthy.")
    else:
        for issue in report.issues:
            lines.append(f"  {issue}")
        lines.append("")
        lines.append(
            f"  {report.error_count} error(s), {report.warning_count} warning(s)"
        )
    return "\n".join(lines)
