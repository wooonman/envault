"""Tests for envault.env_copy_all (bulk copy between vaults)."""

import json
import pytest

from envault.vault import save_vault, load_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64
from envault.env_copy_all import bulk_copy, BulkCopyError


PASSWORD = "test-pass"
ALT_PASSWORD = "other-pass"


@pytest.fixture()
def src_vault(tmp_path):
    path = str(tmp_path / "src.vault.json")
    data = {
        "KEY_A": encrypt_to_b64("alpha", PASSWORD),
        "KEY_B": encrypt_to_b64("beta", PASSWORD),
    }
    save_vault(path, data)
    return path


@pytest.fixture()
def dest_vault(tmp_path):
    path = str(tmp_path / "dest.vault.json")
    save_vault(path, {})
    return path


def test_bulk_copy_copies_all_keys(src_vault, dest_vault):
    result = bulk_copy(src_vault, dest_vault, PASSWORD, PASSWORD)
    assert sorted(result.copied) == ["KEY_A", "KEY_B"]
    assert result.skipped == []


def test_bulk_copy_values_are_decryptable(src_vault, dest_vault):
    bulk_copy(src_vault, dest_vault, PASSWORD, PASSWORD)
    vault = load_vault(dest_vault)
    assert decrypt_from_b64(vault["KEY_A"], PASSWORD) == "alpha"
    assert decrypt_from_b64(vault["KEY_B"], PASSWORD) == "beta"


def test_bulk_copy_with_prefix(src_vault, dest_vault):
    result = bulk_copy(src_vault, dest_vault, PASSWORD, PASSWORD, prefix="PROD_")
    assert "PROD_KEY_A" in result.copied
    assert "PROD_KEY_B" in result.copied
    vault = load_vault(dest_vault)
    assert "PROD_KEY_A" in vault
    assert "KEY_A" not in vault


def test_bulk_copy_with_suffix(src_vault, dest_vault):
    result = bulk_copy(src_vault, dest_vault, PASSWORD, PASSWORD, suffix="_V2")
    assert "KEY_A_V2" in result.copied


def test_bulk_copy_skips_existing_without_overwrite(src_vault, dest_vault):
    # Pre-populate dest with KEY_A
    dest = load_vault(dest_vault)
    dest["KEY_A"] = encrypt_to_b64("old", PASSWORD)
    save_vault(dest_vault, dest)

    result = bulk_copy(src_vault, dest_vault, PASSWORD, PASSWORD, overwrite=False)
    assert "KEY_A" in result.skipped
    assert "KEY_B" in result.copied


def test_bulk_copy_overwrites_existing_when_flag_set(src_vault, dest_vault):
    dest = load_vault(dest_vault)
    dest["KEY_A"] = encrypt_to_b64("old", PASSWORD)
    save_vault(dest_vault, dest)

    result = bulk_copy(src_vault, dest_vault, PASSWORD, PASSWORD, overwrite=True)
    assert "KEY_A" in result.copied
    assert "KEY_A" not in result.skipped

    vault = load_vault(dest_vault)
    assert decrypt_from_b64(vault["KEY_A"], PASSWORD) == "alpha"


def test_bulk_copy_different_passwords(src_vault, dest_vault):
    bulk_copy(src_vault, dest_vault, PASSWORD, ALT_PASSWORD)
    vault = load_vault(dest_vault)
    assert decrypt_from_b64(vault["KEY_A"], ALT_PASSWORD) == "alpha"


def test_bulk_copy_wrong_src_password_raises(src_vault, dest_vault):
    with pytest.raises(BulkCopyError):
        bulk_copy(src_vault, dest_vault, "wrong", PASSWORD)


def test_bulk_copy_str_result(src_vault, dest_vault):
    result = bulk_copy(src_vault, dest_vault, PASSWORD, PASSWORD)
    text = str(result)
    assert "Copied" in text
    assert src_vault in text
    assert dest_vault in text
