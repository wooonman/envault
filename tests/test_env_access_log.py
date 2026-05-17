"""Tests for envault.env_access_log"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64
from envault.env_access_log import (
    AccessEntry,
    format_access_log,
    get_access_log,
    record_access,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.json"
    vault = {
        "API_KEY": encrypt_to_b64("secret", PASSWORD),
        "DB_URL": encrypt_to_b64("postgres://localhost/db", PASSWORD),
    }
    save_vault(path, vault)
    return path


def test_record_access_returns_entry(vault_file: Path) -> None:
    entry = record_access(vault_file, "API_KEY", "read")
    assert isinstance(entry, AccessEntry)
    assert entry.key == "API_KEY"
    assert entry.action == "read"
    assert entry.timestamp


def test_record_access_persists_to_vault(vault_file: Path) -> None:
    record_access(vault_file, "API_KEY", "write")
    entries = get_access_log(vault_file)
    assert len(entries) == 1
    assert entries[0].action == "write"


def test_record_access_multiple_entries(vault_file: Path) -> None:
    record_access(vault_file, "API_KEY", "read")
    record_access(vault_file, "DB_URL", "read")
    record_access(vault_file, "API_KEY", "delete")
    entries = get_access_log(vault_file)
    assert len(entries) == 3


def test_get_access_log_filter_by_key(vault_file: Path) -> None:
    record_access(vault_file, "API_KEY", "read")
    record_access(vault_file, "DB_URL", "write")
    entries = get_access_log(vault_file, key="API_KEY")
    assert all(e.key == "API_KEY" for e in entries)
    assert len(entries) == 1


def test_get_access_log_filter_by_action(vault_file: Path) -> None:
    record_access(vault_file, "API_KEY", "read")
    record_access(vault_file, "DB_URL", "write")
    record_access(vault_file, "API_KEY", "read")
    entries = get_access_log(vault_file, action="read")
    assert len(entries) == 2
    assert all(e.action == "read" for e in entries)


def test_get_access_log_empty_vault(vault_file: Path) -> None:
    entries = get_access_log(vault_file)
    assert entries == []


def test_record_access_invalid_action_raises(vault_file: Path) -> None:
    with pytest.raises(ValueError, match="Unknown action"):
        record_access(vault_file, "API_KEY", "peek")


def test_format_access_log_empty() -> None:
    assert format_access_log([]) == "No access log entries."


def test_format_access_log_shows_entries(vault_file: Path) -> None:
    record_access(vault_file, "API_KEY", "read")
    entries = get_access_log(vault_file)
    output = format_access_log(entries)
    assert "API_KEY" in output
    assert "READ" in output


def test_access_entry_str() -> None:
    e = AccessEntry(key="MY_KEY", action="write", timestamp="2024-01-01T00:00:00")
    s = str(e)
    assert "MY_KEY" in s
    assert "WRITE" in s
    assert "2024-01-01" in s
