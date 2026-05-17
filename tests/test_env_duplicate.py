"""Tests for envault.env_duplicate."""
import json
import pytest

from envault.crypto import encrypt_to_b64
from envault.env_duplicate import find_duplicates, DuplicateResult, DuplicateGroup


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    entries = {
        "DB_PASS": encrypt_to_b64("secret", PASSWORD),
        "DB_PASSWORD": encrypt_to_b64("secret", PASSWORD),
        "API_KEY": encrypt_to_b64("unique1", PASSWORD),
        "BACKUP_KEY": encrypt_to_b64("unique1", PASSWORD),
        "TOKEN": encrypt_to_b64("only_once", PASSWORD),
    }
    data = {"entries": entries}
    p = tmp_path / "vault.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_find_duplicates_returns_result(vault_file):
    result = find_duplicates(vault_file, PASSWORD)
    assert isinstance(result, DuplicateResult)


def test_find_duplicates_detects_groups(vault_file):
    result = find_duplicates(vault_file, PASSWORD)
    assert result.has_duplicates
    assert len(result.groups) == 2


def test_find_duplicates_group_keys_sorted(vault_file):
    result = find_duplicates(vault_file, PASSWORD)
    for group in result.groups:
        assert group.keys == sorted(group.keys)


def test_find_duplicates_correct_keys(vault_file):
    result = find_duplicates(vault_file, PASSWORD)
    all_key_sets = [set(g.keys) for g in result.groups]
    assert {"DB_PASS", "DB_PASSWORD"} in all_key_sets
    assert {"API_KEY", "BACKUP_KEY"} in all_key_sets


def test_find_duplicates_no_duplicate(tmp_path):
    entries = {
        "A": encrypt_to_b64("val1", PASSWORD),
        "B": encrypt_to_b64("val2", PASSWORD),
    }
    p = tmp_path / "vault.json"
    p.write_text(json.dumps({"entries": entries}))
    result = find_duplicates(str(p), PASSWORD)
    assert not result.has_duplicates
    assert result.groups == []


def test_total_affected_keys(vault_file):
    result = find_duplicates(vault_file, PASSWORD)
    assert result.total_affected_keys == 4


def test_str_no_duplicates(tmp_path):
    entries = {"X": encrypt_to_b64("only", PASSWORD)}
    p = tmp_path / "vault.json"
    p.write_text(json.dumps({"entries": entries}))
    result = find_duplicates(str(p), PASSWORD)
    assert "No duplicate" in str(result)


def test_str_with_duplicates(vault_file):
    result = find_duplicates(vault_file, PASSWORD)
    output = str(result)
    assert "duplicate" in output.lower()
    assert "DB_PASS" in output or "API_KEY" in output


def test_wrong_password_skips_entries(vault_file):
    result = find_duplicates(vault_file, "wrongpass")
    assert not result.has_duplicates
