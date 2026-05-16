"""Tests for envault.env_merge_keys."""

import json
import pytest

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64
from envault.env_merge_keys import merge_keys, MergeKeysError, MergeKeysResult


SRC_PASS = "src-secret"
DEST_PASS = "dest-secret"


def _make_vault(tmp_path, name, password, entries: dict) -> str:
    path = str(tmp_path / name)
    encrypted = {k: encrypt_to_b64(v, password) for k, v in entries.items()}
    save_vault(path, {"entries": encrypted})
    return path


@pytest.fixture
def src_vault(tmp_path):
    return _make_vault(tmp_path, "src.vault", SRC_PASS, {
        "API_KEY": "abc123",
        "DB_URL": "postgres://localhost/dev",
        "SECRET": "topsecret",
    })


@pytest.fixture
def dest_vault(tmp_path):
    return _make_vault(tmp_path, "dest.vault", DEST_PASS, {
        "EXISTING": "already-here",
    })


def test_merge_keys_copies_specified_keys(src_vault, dest_vault):
    result = merge_keys(src_vault, dest_vault, ["API_KEY", "DB_URL"], SRC_PASS, DEST_PASS)
    assert "API_KEY" in result.copied
    assert "DB_URL" in result.copied


def test_merge_keys_values_decryptable_with_dest_password(src_vault, dest_vault):
    merge_keys(src_vault, dest_vault, ["API_KEY"], SRC_PASS, DEST_PASS)
    vault = load_vault(dest_vault)
    val = decrypt_from_b64(vault["entries"]["API_KEY"], DEST_PASS)
    assert val == "abc123"


def test_merge_keys_missing_key_recorded(src_vault, dest_vault):
    result = merge_keys(src_vault, dest_vault, ["NONEXISTENT"], SRC_PASS, DEST_PASS)
    assert "NONEXISTENT" in result.missing


def test_merge_keys_skips_existing_without_overwrite(src_vault, dest_vault):
    merge_keys(src_vault, dest_vault, ["API_KEY"], SRC_PASS, DEST_PASS)
    result = merge_keys(src_vault, dest_vault, ["API_KEY"], SRC_PASS, DEST_PASS, overwrite=False)
    assert "API_KEY" in result.skipped


def test_merge_keys_overwrites_when_flag_set(src_vault, dest_vault):
    merge_keys(src_vault, dest_vault, ["API_KEY"], SRC_PASS, DEST_PASS)
    result = merge_keys(src_vault, dest_vault, ["API_KEY"], SRC_PASS, DEST_PASS, overwrite=True)
    assert "API_KEY" in result.overwritten


def test_merge_keys_preserves_existing_dest_entries(src_vault, dest_vault):
    merge_keys(src_vault, dest_vault, ["API_KEY"], SRC_PASS, DEST_PASS)
    vault = load_vault(dest_vault)
    assert "EXISTING" in vault["entries"]
    val = decrypt_from_b64(vault["entries"]["EXISTING"], DEST_PASS)
    assert val == "already-here"


def test_merge_keys_wrong_src_password_raises(src_vault, dest_vault):
    with pytest.raises(MergeKeysError, match="Failed to decrypt"):
        merge_keys(src_vault, dest_vault, ["API_KEY"], "wrong-pass", DEST_PASS)


def test_merge_keys_str_output_includes_copied(src_vault, dest_vault):
    result = merge_keys(src_vault, dest_vault, ["SECRET"], SRC_PASS, DEST_PASS)
    text = str(result)
    assert "SECRET" in text
    assert "Copied" in text


def test_merge_keys_str_empty_result():
    r = MergeKeysResult()
    assert str(r) == "Nothing to merge."
