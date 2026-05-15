"""Tests for envault.env_grep."""

from __future__ import annotations

import json
import pytest

from envault.env_grep import grep_vault, GrepError, format_grep_report, GrepResult, GrepMatch
from envault.vault import lock


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "API_KEY=supersecret\n"
        "DEBUG=false\n"
        "SECRET_TOKEN=abc123\n"
    )
    vault_path = str(tmp_path / "vault.json")
    lock(str(env_file), vault_path, PASSWORD)
    return vault_path


def test_grep_finds_matching_value(vault_file):
    result = grep_vault(vault_file, PASSWORD, "localhost")
    assert result.count == 1
    assert result.matches[0].key == "DB_HOST"


def test_grep_finds_multiple_matches(vault_file):
    result = grep_vault(vault_file, PASSWORD, "5")
    keys = {m.key for m in result.matches}
    assert "DB_PORT" in keys


def test_grep_no_match_returns_empty(vault_file):
    result = grep_vault(vault_file, PASSWORD, "ZZZNOMATCH")
    assert result.count == 0


def test_grep_ignore_case(vault_file):
    result = grep_vault(vault_file, PASSWORD, "LOCALHOST", ignore_case=True)
    assert result.count == 1
    assert result.matches[0].key == "DB_HOST"


def test_grep_keys_only(vault_file):
    result = grep_vault(vault_file, PASSWORD, "DB", keys_only=True)
    keys = {m.key for m in result.matches}
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "API_KEY" not in keys


def test_grep_invert(vault_file):
    result = grep_vault(vault_file, PASSWORD, "localhost")
    inverted = grep_vault(vault_file, PASSWORD, "localhost", invert=True)
    total = result.count + inverted.count
    assert total == 5  # total entries


def test_grep_regex(vault_file):
    result = grep_vault(vault_file, PASSWORD, r"^\d+$", use_regex=True)
    assert result.count >= 1
    keys = {m.key for m in result.matches}
    assert "DB_PORT" in keys


def test_grep_invalid_regex_raises(vault_file):
    with pytest.raises(GrepError, match="Invalid regex"):
        grep_vault(vault_file, PASSWORD, "[", use_regex=True)


def test_format_grep_report_no_matches():
    result = GrepResult(pattern="xyz")
    report = format_grep_report(result)
    assert "No matches" in report


def test_format_grep_report_with_matches():
    result = GrepResult(
        pattern="test",
        matches=[GrepMatch(key="FOO", value="testval", line_number=1)],
    )
    report = format_grep_report(result, show_line_numbers=True)
    assert "FOO=testval" in report
    assert "1:" in report


def test_grep_wrong_password_skips_entries(vault_file):
    # Wrong password: decrypt fails silently, no matches returned
    result = grep_vault(vault_file, "wrongpass", "localhost")
    assert result.count == 0
