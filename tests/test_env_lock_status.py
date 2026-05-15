"""Tests for envault.env_lock_status."""

from __future__ import annotations

import json
import pytest

from envault.env_lock_status import (
    LockStatusEntry,
    LockStatusResult,
    check_lock_status,
    format_status_report,
)
from envault.vault import lock
from envault.crypto import encrypt_to_b64


@pytest.fixture()
def vault_file(tmp_path):
    path = tmp_path / ".envault"
    lock(str(tmp_path / ".env"), str(path), "secret")
    env = tmp_path / ".env"
    env.write_text("KEY1=hello\nKEY2=world\n")
    lock(str(env), str(path), "secret")
    return str(path)


def test_check_lock_status_returns_result(vault_file):
    result = check_lock_status(vault_file)
    assert isinstance(result, LockStatusResult)
    assert result.total >= 1


def test_all_entries_encrypted(vault_file):
    result = check_lock_status(vault_file)
    assert result.encrypted_count == result.total


def test_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        check_lock_status(str(tmp_path / "nonexistent.vault"))


def test_empty_vault_format(tmp_path):
    path = tmp_path / "empty.vault"
    path.write_text(json.dumps({"entries": {}}))
    result = check_lock_status(str(path))
    assert result.total == 0
    assert format_status_report(result) == "Vault is empty."


def test_lock_status_entry_str_encrypted():
    entry = LockStatusEntry(
        key="DB_PASS",
        is_encrypted=True,
        has_tags=False,
        has_note=False,
        is_pinned=False,
        is_archived=False,
    )
    assert "encrypted" in str(entry)
    assert "DB_PASS" in str(entry)


def test_lock_status_entry_str_plain():
    entry = LockStatusEntry(
        key="API_KEY",
        is_encrypted=False,
        has_tags=False,
        has_note=False,
        is_pinned=False,
        is_archived=False,
    )
    assert "plain" in str(entry)


def test_lock_status_entry_str_with_flags():
    entry = LockStatusEntry(
        key="TOKEN",
        is_encrypted=True,
        has_tags=True,
        has_note=True,
        is_pinned=True,
        is_archived=False,
    )
    text = str(entry)
    assert "tagged" in text
    assert "noted" in text
    assert "pinned" in text


def test_result_str_includes_summary(vault_file):
    result = check_lock_status(vault_file)
    text = str(result)
    assert "Total:" in text
    assert "Encrypted:" in text


def test_format_report_non_empty(vault_file):
    result = check_lock_status(vault_file)
    report = format_status_report(result)
    assert len(report) > 0
    assert "Total:" in report
