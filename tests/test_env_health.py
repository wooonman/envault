"""Tests for envault/env_health.py"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from envault.vault import lock, load_vault, save_vault
from envault.env_health import run_health_check, HealthReport, HealthIssue


PASSWORD = "hunter2"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / ".env.vault"
    lock(str(tmp_path / ".env"), str(vf), PASSWORD, env_text="FOO=bar\nBAZ=qux\n")
    return vf


def test_health_check_returns_report(vault_file: Path) -> None:
    report = run_health_check(str(vault_file), PASSWORD)
    assert isinstance(report, HealthReport)


def test_healthy_vault_has_no_errors(vault_file: Path) -> None:
    report = run_health_check(str(vault_file), PASSWORD)
    assert report.ok
    assert report.error_count == 0


def test_missing_vault_is_error(tmp_path: Path) -> None:
    report = run_health_check(str(tmp_path / "nonexistent.vault"), PASSWORD)
    assert not report.ok
    assert report.error_count >= 1
    categories = [i.category for i in report.issues]
    assert "vault" in categories


def test_empty_vault_produces_info(tmp_path: Path) -> None:
    vf = tmp_path / ".env.vault"
    save_vault(str(vf), {})
    report = run_health_check(str(vf), PASSWORD)
    info_issues = [i for i in report.issues if i.severity == "info"]
    assert any("empty" in i.message.lower() for i in info_issues)


def test_expired_ttl_produces_warning(vault_file: Path) -> None:
    vault = load_vault(str(vault_file))
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    vault.setdefault("__ttl__", {})["FOO"] = {"expires_at": past}
    save_vault(str(vault_file), vault)

    report = run_health_check(str(vault_file), PASSWORD)
    warning_msgs = [i.message for i in report.issues if i.severity == "warning"]
    assert any("FOO" in m for m in warning_msgs)


def test_health_issue_str() -> None:
    issue = HealthIssue(severity="error", category="encryption", message="bad")
    assert "ERROR" in str(issue)
    assert "encryption" in str(issue)
    assert "bad" in str(issue)


def test_format_report_all_clear(vault_file: Path) -> None:
    report = run_health_check(str(vault_file), PASSWORD)
    text = str(report)
    assert str(vault_file) in text


def test_warning_count_property(vault_file: Path) -> None:
    vault = load_vault(str(vault_file))
    past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    vault.setdefault("__ttl__", {})["BAZ"] = {"expires_at": past}
    save_vault(str(vault_file), vault)

    report = run_health_check(str(vault_file), PASSWORD)
    assert report.warning_count >= 1
