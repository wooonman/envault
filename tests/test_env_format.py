"""Tests for envault/env_format.py"""

from __future__ import annotations

import json
import pytest

from envault.vault import load_vault, save_vault
from envault.lock_unlock_helpers import _make_vault
from envault.env_format import format_keys, FormatError, _normalize_key


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault.json")
    vault = _make_vault(
        {"db_host": "localhost", "db_port": "5432", "api_key": "secret"},
        PASSWORD,
    )
    save_vault(path, vault)
    return path


def test_normalize_key_upper():
    assert _normalize_key("db_host", "upper") == "DB_HOST"


def test_normalize_key_lower():
    assert _normalize_key("DB_HOST", "lower") == "db_host"


def test_normalize_key_snake():
    assert _normalize_key("db-host name", "snake") == "DB_HOST_NAME"


def test_normalize_key_unknown_style_raises():
    with pytest.raises(FormatError, match="Unknown style"):
        _normalize_key("KEY", "camel")


def test_format_keys_renames_to_upper(vault_file):
    result = format_keys(vault_file, PASSWORD, style="upper")
    assert any(new == "DB_HOST" for _, new in result.renamed)
    assert any(new == "API_KEY" for _, new in result.renamed)


def test_format_keys_persists_changes(vault_file):
    format_keys(vault_file, PASSWORD, style="upper")
    vault = load_vault(vault_file)
    keys = list(vault["entries"].keys())
    assert "DB_HOST" in keys
    assert "db_host" not in keys


def test_format_keys_skips_already_normalized(vault_file):
    # first pass normalizes everything
    format_keys(vault_file, PASSWORD, style="upper")
    # second pass should skip all
    result = format_keys(vault_file, PASSWORD, style="upper")
    assert result.renamed == []
    assert len(result.skipped) == 3


def test_format_keys_dry_run_does_not_write(vault_file):
    result = format_keys(vault_file, PASSWORD, style="upper", dry_run=True)
    assert result.renamed  # changes detected
    vault = load_vault(vault_file)
    # keys should still be lowercase
    assert "db_host" in vault["entries"]


def test_format_keys_conflict_skipped(tmp_path):
    """If normalizing a key would collide with an existing key, skip it."""
    path = str(tmp_path / "conflict.vault.json")
    vault = _make_vault({"key": "v1", "KEY": "v2"}, PASSWORD)
    save_vault(path, vault)
    result = format_keys(path, PASSWORD, style="upper")
    # 'KEY' already exists; 'key' -> 'KEY' would collide, so it's skipped
    assert "key" in result.skipped or "KEY" in result.skipped


def test_format_result_str_shows_renamed(vault_file):
    result = format_keys(vault_file, PASSWORD, style="upper")
    text = str(result)
    assert "Reformatted" in text


def test_format_result_str_no_changes():
    from envault.env_format import FormatResult
    r = FormatResult(skipped=["A", "B"])
    assert "No keys needed" in str(r)
