"""Tests for envault.vault lock/unlock operations."""

import json
import pytest
from pathlib import Path

from envault.vault import lock, unlock, load_vault, save_vault


PASSWORD = "vault-test-password"
ENV_CONTENT = "API_KEY=test123\nDEBUG=true\n"


@pytest.fixture
def tmp_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(ENV_CONTENT)
    return str(env_file)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / ".env.vault")


def test_lock_creates_vault_file(tmp_env, tmp_vault):
    lock(tmp_env, PASSWORD, tmp_vault)
    assert Path(tmp_vault).exists()


def test_lock_stores_entry(tmp_env, tmp_vault):
    lock(tmp_env, PASSWORD, tmp_vault)
    vault = load_vault(tmp_vault)
    assert tmp_env in vault
    assert "encrypted" in vault[tmp_env]


def test_lock_unlock_roundtrip(tmp_env, tmp_vault):
    lock(tmp_env, PASSWORD, tmp_vault)
    Path(tmp_env).unlink()  # remove original
    unlock(tmp_env, PASSWORD, tmp_vault)
    assert Path(tmp_env).read_text() == ENV_CONTENT


def test_lock_missing_file_raises(tmp_vault):
    with pytest.raises(FileNotFoundError):
        lock("/nonexistent/.env", PASSWORD, tmp_vault)


def test_unlock_missing_entry_raises(tmp_vault):
    save_vault({}, tmp_vault)
    with pytest.raises(KeyError):
        unlock(".env", PASSWORD, tmp_vault)


def test_unlock_wrong_password_raises(tmp_env, tmp_vault):
    lock(tmp_env, PASSWORD, tmp_vault)
    with pytest.raises(Exception):
        unlock(tmp_env, "wrong-password", tmp_vault)
