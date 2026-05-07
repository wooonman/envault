"""Tests for envault.rename."""

from __future__ import annotations

import json
import pytest

from envault.vault import load_vault, save_vault, lock
from envault.rename import rename_key, format_rename_report, RenameError


PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    env = tmp_path / ".env"
    env.write_text("FOO=bar\nBAZ=qux\n")
    lock(str(env), path, PASSWORD)
    return path


def test_rename_key_changes_name(vault_file):
    rename_key(vault_file, "FOO", "FOO_NEW", PASSWORD)
    vault = load_vault(vault_file)
    assert "FOO_NEW" in vault
    assert "FOO" not in vault


def test_rename_preserves_value(vault_file):
    from envault.crypto import decrypt_from_b64
    rename_key(vault_file, "FOO", "FOO2", PASSWORD)
    vault = load_vault(vault_file)
    plaintext = decrypt_from_b64(vault["FOO2"]["value"], PASSWORD)
    assert plaintext == b"bar"


def test_rename_missing_key_raises(vault_file):
    with pytest.raises(RenameError, match="not found"):
        rename_key(vault_file, "DOES_NOT_EXIST", "X", PASSWORD)


def test_rename_same_key_raises(vault_file):
    with pytest.raises(RenameError, match="identical"):
        rename_key(vault_file, "FOO", "FOO", PASSWORD)


def test_rename_existing_key_raises_without_overwrite(vault_file):
    with pytest.raises(RenameError, match="already exists"):
        rename_key(vault_file, "FOO", "BAZ", PASSWORD)


def test_rename_overwrite_replaces_key(vault_file):
    from envault.crypto import decrypt_from_b64
    rename_key(vault_file, "FOO", "BAZ", PASSWORD, overwrite=True)
    vault = load_vault(vault_file)
    assert "FOO" not in vault
    plaintext = decrypt_from_b64(vault["BAZ"]["value"], PASSWORD)
    assert plaintext == b"bar"


def test_copy_keeps_original(vault_file):
    rename_key(vault_file, "FOO", "FOO_COPY", PASSWORD, copy=True)
    vault = load_vault(vault_file)
    assert "FOO" in vault
    assert "FOO_COPY" in vault


def test_format_rename_report_rename():
    result = {"old_key": "A", "new_key": "B", "action": "rename"}
    assert format_rename_report(result) == "Renamed 'A' -> 'B'"


def test_format_rename_report_copy():
    result = {"old_key": "A", "new_key": "B", "action": "copy"}
    assert format_rename_report(result) == "Copied 'A' -> 'B'"
