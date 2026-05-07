"""Tests for envault.compare — cross-vault diff."""

import json
import pytest

from envault.crypto import encrypt_to_b64
from envault.compare import compare_vaults, format_compare_report


PASSWORD = "test-secret"


def _make_vault(tmp_path, name: str, entries: dict) -> str:
    """Write a minimal vault JSON file and return its path."""
    vault = {
        key: {"ciphertext": encrypt_to_b64(value, PASSWORD)}
        for key, value in entries.items()
    }
    path = tmp_path / name
    path.write_text(json.dumps(vault))
    return str(path)


@pytest.fixture()
def vault_a(tmp_path):
    return _make_vault(tmp_path, "a.vault.json", {"FOO": "bar", "SHARED": "same"})


@pytest.fixture()
def vault_b(tmp_path):
    return _make_vault(
        tmp_path, "b.vault.json", {"BAZ": "qux", "SHARED": "same"}
    )


@pytest.fixture()
def vault_changed(tmp_path):
    return _make_vault(
        tmp_path, "c.vault.json", {"FOO": "NEW", "SHARED": "same"}
    )


def test_compare_identical_vaults_returns_only_unchanged(tmp_path):
    path = _make_vault(tmp_path, "x.vault.json", {"KEY": "val"})
    diffs = compare_vaults(path, path, PASSWORD)
    statuses = {d[0] for d in diffs}
    assert statuses == {"unchanged"}


def test_compare_detects_added_key(vault_a, vault_b):
    diffs = compare_vaults(vault_a, vault_b, PASSWORD)
    added = [d for d in diffs if d[0] == "added"]
    assert any(d[1] == "BAZ" for d in added)


def test_compare_detects_removed_key(vault_a, vault_b):
    diffs = compare_vaults(vault_a, vault_b, PASSWORD)
    removed = [d for d in diffs if d[0] == "removed"]
    assert any(d[1] == "FOO" for d in removed)


def test_compare_detects_changed_value(vault_a, vault_changed):
    diffs = compare_vaults(vault_a, vault_changed, PASSWORD)
    changed = [d for d in diffs if d[0] == "changed"]
    assert any(d[1] == "FOO" for d in changed)


def test_compare_wrong_password_raises(vault_a, vault_b):
    with pytest.raises(ValueError, match="wrong password"):
        compare_vaults(vault_a, vault_b, "bad-password")


def test_format_compare_report_no_diff(tmp_path):
    path = _make_vault(tmp_path, "same.vault.json", {"X": "1"})
    diffs = compare_vaults(path, path, PASSWORD)
    report = format_compare_report(diffs, "old", "new")
    assert "--- old" in report
    assert "+++ new" in report
    assert "(no differences)" in report


def test_format_compare_report_shows_changes(vault_a, vault_changed):
    diffs = compare_vaults(vault_a, vault_changed, PASSWORD)
    report = format_compare_report(diffs)
    assert "FOO" in report
