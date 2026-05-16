"""Tests for envault.env_trim."""
import json
import pytest

from envault.env_trim import trim_entries, TrimError
from envault.vault import load_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.json"
    entries = {
        "CLEAN_KEY": encrypt_to_b64("no_spaces", PASSWORD),
        "DIRTY_KEY": encrypt_to_b64("  has spaces  ", PASSWORD),
        "TABS_KEY": encrypt_to_b64("\tleading tab", PASSWORD),
        "BOTH_KEY": encrypt_to_b64(" \n padded \n ", PASSWORD),
    }
    path.write_text(json.dumps({"entries": entries}))
    return str(path)


def test_trim_clean_key_is_skipped(vault_file):
    result = trim_entries(vault_file, PASSWORD, keys=["CLEAN_KEY"])
    assert "CLEAN_KEY" in result.skipped
    assert "CLEAN_KEY" not in result.trimmed


def test_trim_dirty_key_is_trimmed(vault_file):
    result = trim_entries(vault_file, PASSWORD, keys=["DIRTY_KEY"])
    assert "DIRTY_KEY" in result.trimmed
    assert "DIRTY_KEY" not in result.skipped


def test_trim_updates_value_in_vault(vault_file):
    trim_entries(vault_file, PASSWORD, keys=["DIRTY_KEY"])
    vault = load_vault(vault_file)
    decrypted = decrypt_from_b64(vault["entries"]["DIRTY_KEY"], PASSWORD)
    assert decrypted == "has spaces"


def test_trim_tabs_key(vault_file):
    trim_entries(vault_file, PASSWORD, keys=["TABS_KEY"])
    vault = load_vault(vault_file)
    decrypted = decrypt_from_b64(vault["entries"]["TABS_KEY"], PASSWORD)
    assert decrypted == "leading tab"


def test_trim_all_keys_by_default(vault_file):
    result = trim_entries(vault_file, PASSWORD)
    assert set(result.trimmed) == {"DIRTY_KEY", "TABS_KEY", "BOTH_KEY"}
    assert result.skipped == ["CLEAN_KEY"]


def test_trim_missing_key_raises(vault_file):
    with pytest.raises(TrimError, match="NOT_EXIST"):
        trim_entries(vault_file, PASSWORD, keys=["NOT_EXIST"])


def test_trim_dry_run_does_not_modify_vault(vault_file):
    vault_before = load_vault(vault_file)
    original_val = vault_before["entries"]["DIRTY_KEY"]

    result = trim_entries(vault_file, PASSWORD, keys=["DIRTY_KEY"], dry_run=True)

    assert "DIRTY_KEY" in result.trimmed
    vault_after = load_vault(vault_file)
    assert vault_after["entries"]["DIRTY_KEY"] == original_val


def test_trim_result_str_with_trimmed(vault_file):
    result = trim_entries(vault_file, PASSWORD, keys=["DIRTY_KEY"])
    text = str(result)
    assert "Trimmed" in text
    assert "DIRTY_KEY" in text


def test_trim_result_str_no_changes(vault_file):
    result = trim_entries(vault_file, PASSWORD, keys=["CLEAN_KEY"])
    text = str(result)
    assert "No keys needed trimming" in text
