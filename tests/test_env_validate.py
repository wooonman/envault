"""Tests for envault/env_validate.py"""

import pytest
from envault.vault import lock
from envault.env_validate import (
    validate_vault,
    format_validation_report,
    ValidationIssue,
    ValidationResult,
)


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("API_KEY=supersecretvalue\nSHORT=hi\nEMPTY=\n")
    vault = tmp_path / ".vault"
    lock(str(env), str(vault), PASSWORD)
    return str(vault)


def test_all_valid_returns_ok(vault_file):
    schema = {"API_KEY": {"required": True, "min_length": 5}}
    result = validate_vault(vault_file, PASSWORD, schema)
    assert result.ok
    assert result.issues == []


def test_missing_required_key_is_error(vault_file):
    schema = {"MISSING_KEY": {"required": True}}
    result = validate_vault(vault_file, PASSWORD, schema)
    assert not result.ok
    assert any(i.key == "MISSING_KEY" and i.rule == "required" for i in result.issues)


def test_missing_optional_key_no_issue(vault_file):
    schema = {"MISSING_KEY": {"required": False}}
    result = validate_vault(vault_file, PASSWORD, schema)
    assert result.ok
    assert result.issues == []


def test_min_length_violation_is_error(vault_file):
    schema = {"SHORT": {"min_length": 10}}
    result = validate_vault(vault_file, PASSWORD, schema)
    assert not result.ok
    assert any(i.key == "SHORT" and i.rule == "min_length" for i in result.issues)


def test_max_length_violation_is_warning(vault_file):
    schema = {"API_KEY": {"max_length": 3}}
    result = validate_vault(vault_file, PASSWORD, schema)
    # warnings do not fail ok
    assert result.ok
    assert any(i.key == "API_KEY" and i.rule == "max_length" and i.severity == "warning"
               for i in result.issues)


def test_pattern_match_passes(vault_file):
    schema = {"API_KEY": {"pattern": r"[a-z]+"}}
    result = validate_vault(vault_file, PASSWORD, schema)
    assert result.ok


def test_pattern_mismatch_is_error(vault_file):
    schema = {"API_KEY": {"pattern": r"\d+"}}
    result = validate_vault(vault_file, PASSWORD, schema)
    assert not result.ok
    assert any(i.rule == "pattern" for i in result.issues)


def test_not_empty_on_empty_value_is_error(vault_file):
    schema = {"EMPTY": {"not_empty": True}}
    result = validate_vault(vault_file, PASSWORD, schema)
    assert not result.ok
    assert any(i.key == "EMPTY" and i.rule == "not_empty" for i in result.issues)


def test_format_report_no_issues():
    result = ValidationResult(issues=[])
    assert "passed" in format_validation_report(result)


def test_format_report_with_issues():
    result = ValidationResult(issues=[
        ValidationIssue("FOO", "required", "key is missing from vault"),
    ])
    report = format_validation_report(result)
    assert "FOO" in report
    assert "error" in report.lower()


def test_validation_issue_str():
    issue = ValidationIssue("BAR", "min_length", "too short", "warning")
    s = str(issue)
    assert "WARNING" in s
    assert "BAR" in s
    assert "min_length" in s
