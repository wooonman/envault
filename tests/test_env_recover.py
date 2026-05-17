"""Tests for envault.env_recover."""

import json
import pytest
from pathlib import Path

from envault.vault import save_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64
from envault.env_recover import recover_entries, RecoverError


BACKUP_PASS = "backup-secret"
VAULT_PASS = "vault-secret"


def _make_vault(tmp_path: Path, filename: str, entries: dict, password: str) -> Path:
    path = tmp_path / filename
    data = {k: encrypt_to_b64(v, password) for k, v in entries.items()}
    save_vault(str(path), data)
    return path


@pytest.fixture
def backup_file(tmp_path):
    return _make_vault(
        tmp_path,
        "backup.json",
        {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "topsecret"},
        BACKUP_PASS,
    )


@pytest.fixture
def vault_file(tmp_path):
    return _make_vault(
        tmp_path,
        "vault.json",
        {"APP_ENV": "production"},
        VAULT_PASS,
    )


def test_recover_all_keys(backup_file, vault_file):
    result = recover_entries(backup_file, vault_file, BACKUP_PASS, VAULT_PASS)
    assert set(result.recovered) == {"DB_HOST", "DB_PORT", "SECRET"}
    assert result.skipped == []
    assert result.overwritten == []


def test_recover_specific_keys(backup_file, vault_file):
    result = recover_entries(backup_file, vault_file, BACKUP_PASS, VAULT_PASS, keys=["DB_HOST"])
    assert result.recovered == ["DB_HOST"]
    assert result.skipped == []


def test_recovered_values_decryptable(backup_file, vault_file):
    recover_entries(backup_file, vault_file, BACKUP_PASS, VAULT_PASS, keys=["DB_HOST"])
    from envault.vault import load_vault
    vault = load_vault(str(vault_file))
    assert decrypt_from_b64(vault["DB_HOST"], VAULT_PASS) == b"localhost"


def test_recover_skips_existing_without_overwrite(backup_file, tmp_path):
    vault = _make_vault(tmp_path, "v2.json", {"DB_HOST": "other"}, VAULT_PASS)
    result = recover_entries(backup_file, vault, BACKUP_PASS, VAULT_PASS, keys=["DB_HOST"])
    assert "DB_HOST" in result.skipped
    assert "DB_HOST" not in result.recovered


def test_recover_overwrites_existing_when_flag_set(backup_file, tmp_path):
    vault = _make_vault(tmp_path, "v3.json", {"DB_HOST": "other"}, VAULT_PASS)
    result = recover_entries(
        backup_file, vault, BACKUP_PASS, VAULT_PASS, keys=["DB_HOST"], overwrite=True
    )
    assert "DB_HOST" in result.overwritten
    from envault.vault import load_vault
    data = load_vault(str(vault))
    assert decrypt_from_b64(data["DB_HOST"], VAULT_PASS) == b"localhost"


def test_recover_missing_backup_raises(tmp_path, vault_file):
    with pytest.raises(RecoverError, match="Backup file not found"):
        recover_entries(tmp_path / "no.json", vault_file, BACKUP_PASS, VAULT_PASS)


def test_recover_key_not_in_backup_raises(backup_file, vault_file):
    with pytest.raises(RecoverError, match="not found in backup"):
        recover_entries(backup_file, vault_file, BACKUP_PASS, VAULT_PASS, keys=["MISSING_KEY"])


def test_recover_wrong_backup_password_raises(backup_file, vault_file):
    with pytest.raises(RecoverError, match="Failed to decrypt"):
        recover_entries(backup_file, vault_file, "wrong-pass", VAULT_PASS, keys=["DB_HOST"])


def test_str_result_recovered():
    from envault.env_recover import RecoverResult
    r = RecoverResult(recovered=["A", "B"], skipped=["C"])
    text = str(r)
    assert "Recovered" in text
    assert "Skipped" in text


def test_str_result_nothing():
    from envault.env_recover import RecoverResult
    r = RecoverResult()
    assert str(r) == "Nothing to recover."
