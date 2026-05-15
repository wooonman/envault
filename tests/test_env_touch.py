"""Tests for envault.env_touch."""

import json
import pytest
from pathlib import Path

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64
from envault.env_touch import touch_key, touch_keys, TouchError, TouchResult, format_touch_report


PASSWORD = "touchpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    entries = {
        "DB_HOST": {"ciphertext": encrypt_to_b64("localhost", PASSWORD)},
        "DB_PORT": {"ciphertext": encrypt_to_b64("5432", PASSWORD)},
    }
    save_vault(path, {"entries": entries})
    return path


def test_touch_key_sets_updated_at(vault_file):
    result = touch_key(vault_file, "DB_HOST", PASSWORD)
    assert "DB_HOST" in result.touched
    vault = load_vault(vault_file)
    assert "updated_at" in vault["entries"]["DB_HOST"]


def test_touch_key_missing_key_is_skipped(vault_file):
    result = touch_key(vault_file, "NONEXISTENT", PASSWORD)
    assert "NONEXISTENT" in result.skipped
    assert result.touched == []


def test_touch_keys_multiple(vault_file):
    result = touch_keys(vault_file, ["DB_HOST", "DB_PORT"], PASSWORD)
    assert set(result.touched) == {"DB_HOST", "DB_PORT"}
    assert result.skipped == []


def test_touch_keys_mixed_found_and_missing(vault_file):
    result = touch_keys(vault_file, ["DB_HOST", "MISSING_KEY"], PASSWORD)
    assert "DB_HOST" in result.touched
    assert "MISSING_KEY" in result.skipped


def test_touch_does_not_alter_ciphertext(vault_file):
    before = load_vault(vault_file)["entries"]["DB_HOST"]["ciphertext"]
    touch_key(vault_file, "DB_HOST", PASSWORD)
    after = load_vault(vault_file)["entries"]["DB_HOST"]["ciphertext"]
    assert before == after


def test_touch_preserves_other_entries(vault_file):
    touch_key(vault_file, "DB_HOST", PASSWORD)
    vault = load_vault(vault_file)
    assert "DB_PORT" in vault["entries"]


def test_format_touch_report_touched(vault_file):
    result = touch_key(vault_file, "DB_HOST", PASSWORD)
    report = format_touch_report(result)
    assert "DB_HOST" in report
    assert "Touched" in report


def test_format_touch_report_skipped(vault_file):
    result = touch_key(vault_file, "GHOST", PASSWORD)
    report = format_touch_report(result)
    assert "GHOST" in report
    assert "Not found" in report


def test_format_touch_report_empty():
    result = TouchResult()
    assert format_touch_report(result) == "Nothing to touch."
