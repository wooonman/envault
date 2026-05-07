"""Tests for envault.delete."""

import pytest

from envault.delete import delete_key, delete_keys, format_delete_report, DeleteError
from envault.vault import load_vault, save_vault, lock


PASSWORD = "hunter2"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    lock(path, PASSWORD, "KEY_A", "value_a")
    lock(path, PASSWORD, "KEY_B", "value_b")
    lock(path, PASSWORD, "KEY_C", "value_c")
    return path


def test_delete_key_removes_entry(vault_file):
    delete_key(vault_file, PASSWORD, "KEY_A")
    vault = load_vault(vault_file)
    assert "KEY_A" not in vault


def test_delete_key_preserves_other_entries(vault_file):
    delete_key(vault_file, PASSWORD, "KEY_A")
    vault = load_vault(vault_file)
    assert "KEY_B" in vault
    assert "KEY_C" in vault


def test_delete_key_returns_removed_entry(vault_file):
    removed = delete_key(vault_file, PASSWORD, "KEY_B")
    assert isinstance(removed, dict)


def test_delete_key_missing_raises(vault_file):
    with pytest.raises(DeleteError, match="MISSING"):
        delete_key(vault_file, PASSWORD, "MISSING")


def test_delete_keys_removes_multiple(vault_file):
    deleted = delete_keys(vault_file, PASSWORD, ["KEY_A", "KEY_C"])
    vault = load_vault(vault_file)
    assert "KEY_A" not in vault
    assert "KEY_C" not in vault
    assert "KEY_B" in vault
    assert set(deleted) == {"KEY_A", "KEY_C"}


def test_delete_keys_missing_raises_no_changes(vault_file):
    with pytest.raises(DeleteError, match="NOPE"):
        delete_keys(vault_file, PASSWORD, ["KEY_A", "NOPE"])
    # vault should be untouched
    vault = load_vault(vault_file)
    assert "KEY_A" in vault


def test_format_delete_report_single():
    report = format_delete_report(["MY_KEY"])
    assert "MY_KEY" in report
    assert "1" in report


def test_format_delete_report_multiple():
    report = format_delete_report(["A", "B", "C"])
    assert "3" in report
    assert "A" in report
    assert "C" in report


def test_format_delete_report_empty():
    report = format_delete_report([])
    assert report == "No keys deleted."
