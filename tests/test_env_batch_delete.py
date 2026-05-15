"""Tests for envault.env_batch_delete."""

import json
import pytest
from pathlib import Path
from envault.vault import load_vault, save_vault
from envault.lock_unlock_helpers import _make_vault
from envault.env_batch_delete import batch_delete, BatchDeleteError, BatchDeleteResult

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    _make_vault(path, {"ALPHA": "aaa", "BETA": "bbb", "GAMMA": "ccc"}, PASSWORD)
    return path


def test_batch_delete_removes_keys(vault_file):
    result = batch_delete(vault_file, ["ALPHA", "BETA"])
    assert "ALPHA" in result.deleted
    assert "BETA" in result.deleted
    vault = load_vault(vault_file)
    assert "ALPHA" not in vault["entries"]
    assert "BETA" not in vault["entries"]
    assert "GAMMA" in vault["entries"]


def test_batch_delete_returns_result_object(vault_file):
    result = batch_delete(vault_file, ["ALPHA"])
    assert isinstance(result, BatchDeleteResult)
    assert result.deleted == ["ALPHA"]
    assert result.missing == []
    assert result.skipped == []


def test_batch_delete_missing_key_raises_by_default(vault_file):
    with pytest.raises(BatchDeleteError, match="NOPE"):
        batch_delete(vault_file, ["NOPE"])


def test_batch_delete_skip_missing_records_missing(vault_file):
    result = batch_delete(vault_file, ["ALPHA", "NOPE"], skip_missing=True)
    assert "ALPHA" in result.deleted
    assert "NOPE" in result.missing


def test_batch_delete_pinned_key_is_skipped_by_default(vault_file):
    vault = load_vault(vault_file)
    vault["_pins"] = ["BETA"]
    save_vault(vault_file, vault)

    result = batch_delete(vault_file, ["ALPHA", "BETA"])
    assert "ALPHA" in result.deleted
    assert "BETA" in result.skipped
    vault2 = load_vault(vault_file)
    assert "BETA" in vault2["entries"]


def test_batch_delete_force_pinned_deletes_pinned(vault_file):
    vault = load_vault(vault_file)
    vault["_pins"] = ["BETA"]
    save_vault(vault_file, vault)

    result = batch_delete(vault_file, ["BETA"], skip_pinned=False)
    assert "BETA" in result.deleted
    vault2 = load_vault(vault_file)
    assert "BETA" not in vault2["entries"]


def test_batch_delete_str_output(vault_file):
    result = batch_delete(vault_file, ["ALPHA", "BETA"])
    text = str(result)
    assert "Deleted" in text
    assert "ALPHA" in text


def test_batch_delete_empty_result_str(vault_file):
    vault = load_vault(vault_file)
    vault["_pins"] = ["ALPHA", "BETA", "GAMMA"]
    save_vault(vault_file, vault)
    result = batch_delete(vault_file, ["ALPHA", "BETA", "GAMMA"])
    assert result.deleted == []
    assert "Nothing" in str(result) or "Skipped" in str(result)
