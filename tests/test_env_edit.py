"""Tests for envault.env_edit."""

import json
import pytest

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64
from envault.env_edit import edit_entry, format_edit_report, EditError, EditResult


PASSWORD = "test-password"


@pytest.fixture()
def vault_file(tmp_path):
    path = tmp_path / ".envault"
    vault = {
        "entries": {
            "DB_HOST": encrypt_to_b64("localhost", PASSWORD),
            "DB_PORT": encrypt_to_b64("5432", PASSWORD),
        }
    }
    save_vault(str(path), vault)
    return str(path)


def test_edit_entry_updates_value(vault_file):
    result = edit_entry(vault_file, "DB_HOST", "remotehost", PASSWORD)
    vault = load_vault(vault_file)
    decrypted = decrypt_from_b64(vault["entries"]["DB_HOST"], PASSWORD)
    assert decrypted == "remotehost"


def test_edit_entry_returns_edit_result(vault_file):
    result = edit_entry(vault_file, "DB_HOST", "newhost", PASSWORD)
    assert isinstance(result, EditResult)
    assert result.key == "DB_HOST"
    assert result.old_value == "localhost"
    assert result.new_value == "newhost"


def test_edit_entry_preserves_other_keys(vault_file):
    edit_entry(vault_file, "DB_HOST", "changed", PASSWORD)
    vault = load_vault(vault_file)
    assert decrypt_from_b64(vault["entries"]["DB_PORT"], PASSWORD) == "5432"


def test_edit_entry_missing_key_raises(vault_file):
    with pytest.raises(EditError, match="not found"):
        edit_entry(vault_file, "MISSING_KEY", "value", PASSWORD)


def test_edit_entry_create_flag_adds_new_key(vault_file):
    result = edit_entry(vault_file, "NEW_KEY", "newval", PASSWORD, create=True)
    vault = load_vault(vault_file)
    assert decrypt_from_b64(vault["entries"]["NEW_KEY"], PASSWORD) == "newval"
    assert result.old_value == ""


def test_edit_entry_wrong_password_raises(vault_file):
    with pytest.raises(Exception):
        edit_entry(vault_file, "DB_HOST", "x", "wrong-password")


def test_format_edit_report_contains_key(vault_file):
    result = edit_entry(vault_file, "DB_PORT", "9999", PASSWORD)
    report = format_edit_report(result)
    assert "DB_PORT" in report
    assert "updated" in report


def test_edit_str_hides_values(vault_file):
    result = edit_entry(vault_file, "DB_HOST", "secret", PASSWORD)
    text = str(result)
    assert "secret" not in text
    assert "localhost" not in text
