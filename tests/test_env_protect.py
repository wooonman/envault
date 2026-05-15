"""Tests for envault/env_protect.py"""

from __future__ import annotations

import json
import pytest

from envault.env_protect import (
    ProtectError,
    assert_not_protected,
    format_protect_report,
    get_protected,
    is_protected,
    protect_key,
    unprotect_key,
)
from envault.vault import save_vault


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    data = {
        "API_KEY": "enc_abc",
        "DB_URL": "enc_def",
        "SECRET": "enc_ghi",
    }
    save_vault(path, data)
    return path


def test_get_protected_empty(vault_file):
    assert get_protected(vault_file) == []


def test_protect_key_adds_to_list(vault_file):
    protect_key(vault_file, "API_KEY")
    assert "API_KEY" in get_protected(vault_file)


def test_protect_key_is_sorted(vault_file):
    protect_key(vault_file, "SECRET")
    protect_key(vault_file, "API_KEY")
    keys = get_protected(vault_file)
    assert keys == sorted(keys)


def test_protect_key_idempotent(vault_file):
    protect_key(vault_file, "API_KEY")
    protect_key(vault_file, "API_KEY")
    assert get_protected(vault_file).count("API_KEY") == 1


def test_protect_missing_key_raises(vault_file):
    with pytest.raises(ProtectError, match="not found"):
        protect_key(vault_file, "NONEXISTENT")


def test_unprotect_key_removes_from_list(vault_file):
    protect_key(vault_file, "DB_URL")
    unprotect_key(vault_file, "DB_URL")
    assert "DB_URL" not in get_protected(vault_file)


def test_unprotect_key_not_protected_raises(vault_file):
    with pytest.raises(ProtectError, match="not protected"):
        unprotect_key(vault_file, "API_KEY")


def test_is_protected_true(vault_file):
    protect_key(vault_file, "SECRET")
    assert is_protected(vault_file, "SECRET") is True


def test_is_protected_false(vault_file):
    assert is_protected(vault_file, "API_KEY") is False


def test_assert_not_protected_raises_when_protected(vault_file):
    protect_key(vault_file, "API_KEY")
    with pytest.raises(ProtectError, match="protected"):
        assert_not_protected(vault_file, "API_KEY", "delete")


def test_assert_not_protected_passes_when_unprotected(vault_file):
    assert_not_protected(vault_file, "DB_URL", "delete")  # should not raise


def test_format_protect_report_empty():
    report = format_protect_report([])
    assert "No protected" in report


def test_format_protect_report_lists_keys():
    report = format_protect_report(["API_KEY", "DB_URL"])
    assert "API_KEY" in report
    assert "DB_URL" in report
    assert "🔒" in report
