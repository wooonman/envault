"""Tests for envault.env_diff_vault."""

import json
import pytest

from envault.vault import lock
from envault.env_diff_vault import diff_vaults, VaultDiffError, format_vault_diff


PASSWORD = "test-pass"


@pytest.fixture()
def vault_a(tmp_path):
    env = tmp_path / "a.env"
    env.write_text("KEY1=alpha\nKEY2=beta\nSHARED=same\n")
    vault = tmp_path / "a.vault.json"
    lock(str(env), str(vault), PASSWORD)
    return str(vault)


@pytest.fixture()
def vault_b(tmp_path):
    env = tmp_path / "b.env"
    env.write_text("KEY2=beta\nKEY3=gamma\nSHARED=same\n")
    vault = tmp_path / "b.vault.json"
    lock(str(env), str(vault), PASSWORD)
    return str(vault)


@pytest.fixture()
def vault_changed(tmp_path):
    env = tmp_path / "c.env"
    env.write_text("KEY1=CHANGED\nKEY2=beta\nSHARED=different\n")
    vault = tmp_path / "c.vault.json"
    lock(str(env), str(vault), PASSWORD)
    return str(vault)


def test_diff_added_keys(vault_a, vault_b):
    result = diff_vaults(vault_a, vault_b, PASSWORD)
    assert "KEY3" in result.added


def test_diff_removed_keys(vault_a, vault_b):
    result = diff_vaults(vault_a, vault_b, PASSWORD)
    assert "KEY1" in result.removed


def test_diff_unchanged_keys(vault_a, vault_b):
    result = diff_vaults(vault_a, vault_b, PASSWORD)
    assert "KEY2" in result.unchanged
    assert "SHARED" in result.unchanged


def test_diff_changed_keys(vault_a, vault_changed):
    result = diff_vaults(vault_a, vault_changed, PASSWORD)
    assert "KEY1" in result.changed
    assert "SHARED" in result.changed


def test_identical_vaults_no_differences(vault_a):
    result = diff_vaults(vault_a, vault_a, PASSWORD)
    assert not result.has_differences()


def test_wrong_password_raises(vault_a, vault_b):
    with pytest.raises(VaultDiffError):
        diff_vaults(vault_a, vault_b, "wrong-password")


def test_missing_vault_raises(vault_a):
    with pytest.raises(FileNotFoundError):
        diff_vaults(vault_a, "/nonexistent/path.vault.json", PASSWORD)


def test_format_vault_diff_symbols(vault_a, vault_b):
    result = diff_vaults(vault_a, vault_b, PASSWORD)
    output = format_vault_diff(result)
    assert "+" in output  # added
    assert "-" in output  # removed


def test_format_vault_diff_empty_result():
    from envault.env_diff_vault import VaultDiffResult
    result = VaultDiffResult()
    assert format_vault_diff(result) == "(no entries)"


def test_format_vault_diff_contains_key_names(vault_a, vault_b):
    """Ensure formatted diff output actually includes the key names."""
    result = diff_vaults(vault_a, vault_b, PASSWORD)
    output = format_vault_diff(result)
    assert "KEY1" in output  # removed key should appear
    assert "KEY3" in output  # added key should appear


def test_different_passwords_per_vault(tmp_path):
    env_a = tmp_path / "a.env"
    env_a.write_text("FOO=bar\n")
    vault_a = tmp_path / "a.vault.json"
    lock(str(env_a), str(vault_a), "pass-a")

    env_b = tmp_path / "b.env"
    env_b.write_text("FOO=bar\n")
    vault_b = tmp_path / "b.vault.json"
    lock(str(env_b), str(vault_b), "pass-b")

    result = diff_vaults(str(vault_a), str(vault_b), "pass-a", "pass-b")
    assert not result.has_differences()
