"""Tests for envault/env_set.py"""

from __future__ import annotations

import json
import pytest

from envault.env_set import set_entry, set_entries, SetError, format_set_report
from envault.vault import load_vault
from envault.crypto import decrypt_from_b64


PASSWORD = "hunter2"


@pytest.fixture()
def vault_file(tmp_path):
    path = tmp_path / ".envault"
    path.write_text(json.dumps({"entries": {}}))
    return str(path)


def test_set_entry_adds_new_key(vault_file):
    result = set_entry(vault_file, "DB_HOST", "localhost", PASSWORD)
    assert result.key == "DB_HOST"
    assert result.overwritten is False


def test_set_entry_value_is_encrypted(vault_file):
    set_entry(vault_file, "SECRET", "mysecret", PASSWORD)
    vault = load_vault(vault_file)
    raw = vault["entries"]["SECRET"]
    assert raw != "mysecret"
    assert decrypt_from_b64(raw, PASSWORD) == "mysecret"


def test_set_entry_overwrite_existing(vault_file):
    set_entry(vault_file, "KEY", "old", PASSWORD)
    result = set_entry(vault_file, "KEY", "new", PASSWORD)
    assert result.overwritten is True
    vault = load_vault(vault_file)
    assert decrypt_from_b64(vault["entries"]["KEY"], PASSWORD) == "new"


def test_set_entry_no_overwrite_raises(vault_file):
    set_entry(vault_file, "KEY", "original", PASSWORD)
    with pytest.raises(SetError, match="already exists"):
        set_entry(vault_file, "KEY", "replacement", PASSWORD, overwrite=False)


def test_set_entry_empty_key_raises(vault_file):
    with pytest.raises(SetError, match="empty"):
        set_entry(vault_file, "", "value", PASSWORD)


def test_set_entry_key_with_equals_raises(vault_file):
    with pytest.raises(SetError, match="'='"):
        set_entry(vault_file, "BAD=KEY", "value", PASSWORD)


def test_set_entries_bulk(vault_file):
    pairs = {"A": "1", "B": "2", "C": "3"}
    results = set_entries(vault_file, pairs, PASSWORD)
    assert len(results) == 3
    vault = load_vault(vault_file)
    for key, val in pairs.items():
        assert decrypt_from_b64(vault["entries"][key], PASSWORD) == val


def test_format_set_report_added(vault_file):
    result = set_entry(vault_file, "X", "y", PASSWORD)
    report = format_set_report([result])
    assert "Added" in report
    assert "X" in report


def test_format_set_report_updated(vault_file):
    set_entry(vault_file, "X", "y", PASSWORD)
    result = set_entry(vault_file, "X", "z", PASSWORD)
    report = format_set_report([result])
    assert "Updated" in report


def test_format_set_report_empty():
    assert format_set_report([]) == "No entries changed."
