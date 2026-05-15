"""Tests for envault.env_rename_bulk."""

from __future__ import annotations

import pytest

from envault.vault import load_vault
from envault.lock_unlock_helpers import _make_vault  # reuse helper pattern below
from envault.env_rename_bulk import bulk_rename_prefix, bulk_rename_map, BulkRenameResult
from envault.crypto import decrypt_from_b64
from envault.vault import lock, unlock

PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    lock(path, "APP_HOST", "localhost", PASSWORD)
    lock(path, "APP_PORT", "8080", PASSWORD)
    lock(path, "DB_HOST", "db.local", PASSWORD)
    lock(path, "DB_PORT", "5432", PASSWORD)
    return path


# --- bulk_rename_prefix ---

def test_prefix_rename_renames_matching_keys(vault_file):
    result = bulk_rename_prefix(vault_file, PASSWORD, "APP_", "SVC_")
    vault = load_vault(vault_file)
    assert "SVC_HOST" in vault
    assert "SVC_PORT" in vault
    assert "APP_HOST" not in vault
    assert "APP_PORT" not in vault


def test_prefix_rename_leaves_non_matching_keys(vault_file):
    bulk_rename_prefix(vault_file, PASSWORD, "APP_", "SVC_")
    vault = load_vault(vault_file)
    assert "DB_HOST" in vault
    assert "DB_PORT" in vault


def test_prefix_rename_preserves_values(vault_file):
    bulk_rename_prefix(vault_file, PASSWORD, "APP_", "SVC_")
    assert unlock(vault_file, "SVC_HOST", PASSWORD) == "localhost"
    assert unlock(vault_file, "SVC_PORT", PASSWORD) == "8080"


def test_prefix_rename_returns_result_object(vault_file):
    result = bulk_rename_prefix(vault_file, PASSWORD, "APP_", "SVC_")
    assert isinstance(result, BulkRenameResult)
    assert len(result.renamed) == 2
    assert len(result.skipped) == 0


def test_prefix_rename_no_match_returns_empty(vault_file):
    result = bulk_rename_prefix(vault_file, PASSWORD, "MISSING_", "X_")
    assert result.renamed == []
    assert result.skipped == []


def test_prefix_rename_dry_run_does_not_write(vault_file):
    result = bulk_rename_prefix(vault_file, PASSWORD, "APP_", "SVC_", dry_run=True)
    vault = load_vault(vault_file)
    # original keys must still exist
    assert "APP_HOST" in vault
    assert len(result.renamed) == 2


def test_prefix_rename_conflict_is_skipped(vault_file):
    # DB_HOST already exists; renaming APP_ -> DB_ should skip APP_HOST
    result = bulk_rename_prefix(vault_file, PASSWORD, "APP_", "DB_")
    assert any(old == "APP_HOST" for old, _ in result.skipped)
    assert any(old == "APP_PORT" for old, _ in result.skipped)


# --- bulk_rename_map ---

def test_map_rename_explicit_pairs(vault_file):
    result = bulk_rename_map(vault_file, PASSWORD, {"APP_HOST": "SERVICE_HOST"})
    vault = load_vault(vault_file)
    assert "SERVICE_HOST" in vault
    assert "APP_HOST" not in vault
    assert len(result.renamed) == 1


def test_map_rename_missing_key_is_skipped(vault_file):
    result = bulk_rename_map(vault_file, PASSWORD, {"NONEXISTENT": "X"})
    assert len(result.skipped) == 1
    assert len(result.renamed) == 0


def test_bulk_rename_result_str_contains_arrows(vault_file):
    result = bulk_rename_prefix(vault_file, PASSWORD, "APP_", "SVC_")
    text = str(result)
    assert "->" in text
