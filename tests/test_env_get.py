"""Tests for envault/env_get.py"""

import json
import pytest

from envault.vault import lock
from envault.env_get import get_entry, get_all_entries, format_get_report, GetError


PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    env = tmp_path / ".env"
    env.write_text("API_KEY=secret123\nDB_PASS=hunter2\n")
    lock(str(env), path, PASSWORD)
    return path


def test_get_entry_returns_correct_value(vault_file):
    result = get_entry(vault_file, "API_KEY", PASSWORD)
    assert result.value == "secret123"
    assert result.key == "API_KEY"
    assert result.found is True


def test_get_entry_another_key(vault_file):
    result = get_entry(vault_file, "DB_PASS", PASSWORD)
    assert result.value == "hunter2"


def test_get_entry_missing_key_raises(vault_file):
    with pytest.raises(GetError, match="does not exist"):
        get_entry(vault_file, "NONEXISTENT", PASSWORD)


def test_get_entry_wrong_password_raises(vault_file):
    with pytest.raises(Exception):
        get_entry(vault_file, "API_KEY", "wrong-password")


def test_get_all_entries_returns_all(vault_file):
    entries = get_all_entries(vault_file, PASSWORD)
    assert entries == {"API_KEY": "secret123", "DB_PASS": "hunter2"}


def test_get_all_entries_empty_vault(tmp_path):
    import json
    path = str(tmp_path / "empty.vault")
    with open(path, "w") as f:
        json.dump({"entries": {}}, f)
    entries = get_all_entries(path, PASSWORD)
    assert entries == {}


def test_format_get_report_masked(vault_file):
    entries = get_all_entries(vault_file, PASSWORD)
    report = format_get_report(entries, reveal=False)
    assert "API_KEY=" in report
    assert "secret123" not in report
    assert "*" in report


def test_format_get_report_revealed(vault_file):
    entries = get_all_entries(vault_file, PASSWORD)
    report = format_get_report(entries, reveal=True)
    assert "API_KEY=secret123" in report
    assert "DB_PASS=hunter2" in report


def test_format_get_report_empty():
    report = format_get_report({})
    assert report == "(no entries)"


def test_get_result_str_returns_value(vault_file):
    result = get_entry(vault_file, "API_KEY", PASSWORD)
    assert str(result) == "secret123"
