"""Tests for envault/env_clone.py"""

from __future__ import annotations

import json
import pytest

from envault.env_clone import clone_key, CloneError, format_clone_report
from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    entries = {
        "DB_URL": encrypt_to_b64(b"postgres://localhost/db", PASSWORD),
        "SECRET": encrypt_to_b64(b"supersecret", PASSWORD),
    }
    save_vault(path, {"entries": entries})
    return path


@pytest.fixture
def second_vault(tmp_path):
    path = str(tmp_path / "vault2.json")
    save_vault(path, {"entries": {}})
    return path


def test_clone_key_within_same_vault(vault_file):
    result = clone_key(vault_file, "DB_URL", vault_file, "DB_URL_COPY", PASSWORD)
    vault = load_vault(vault_file)
    assert "DB_URL_COPY" in vault["entries"]


def test_clone_preserves_value(vault_file):
    clone_key(vault_file, "SECRET", vault_file, "SECRET_BACKUP", PASSWORD)
    vault = load_vault(vault_file)
    decrypted = decrypt_from_b64(vault["entries"]["SECRET_BACKUP"], PASSWORD)
    assert decrypted == b"supersecret"


def test_clone_preserves_original(vault_file):
    clone_key(vault_file, "DB_URL", vault_file, "DB_URL_2", PASSWORD)
    vault = load_vault(vault_file)
    assert "DB_URL" in vault["entries"]


def test_clone_missing_key_raises(vault_file):
    with pytest.raises(CloneError, match="not found"):
        clone_key(vault_file, "MISSING", vault_file, "MISSING_COPY", PASSWORD)


def test_clone_existing_dest_raises_without_overwrite(vault_file):
    with pytest.raises(CloneError, match="already exists"):
        clone_key(vault_file, "DB_URL", vault_file, "SECRET", PASSWORD)


def test_clone_existing_dest_succeeds_with_overwrite(vault_file):
    result = clone_key(
        vault_file, "DB_URL", vault_file, "SECRET", PASSWORD, overwrite=True
    )
    assert result.overwritten is True
    vault = load_vault(vault_file)
    decrypted = decrypt_from_b64(vault["entries"]["SECRET"], PASSWORD)
    assert decrypted == b"postgres://localhost/db"


def test_clone_across_vaults(vault_file, second_vault):
    clone_key(vault_file, "DB_URL", second_vault, "DB_URL", PASSWORD)
    vault2 = load_vault(second_vault)
    assert "DB_URL" in vault2["entries"]
    decrypted = decrypt_from_b64(vault2["entries"]["DB_URL"], PASSWORD)
    assert decrypted == b"postgres://localhost/db"


def test_clone_result_str(vault_file):
    result = clone_key(vault_file, "DB_URL", vault_file, "DB_URL_COPY", PASSWORD)
    text = str(result)
    assert "DB_URL" in text
    assert "DB_URL_COPY" in text


def test_clone_result_overwritten_flag(vault_file):
    r1 = clone_key(vault_file, "DB_URL", vault_file, "NEW_KEY", PASSWORD)
    assert r1.overwritten is False
    r2 = clone_key(
        vault_file, "SECRET", vault_file, "NEW_KEY", PASSWORD, overwrite=True
    )
    assert r2.overwritten is True


def test_format_clone_report(vault_file):
    result = clone_key(vault_file, "DB_URL", vault_file, "DB_COPY", PASSWORD)
    report = format_clone_report(result)
    assert "Cloned" in report
    assert "DB_COPY" in report
