"""Tests for envault.env_count."""

import json
import pytest

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64
from envault.tags import add_tag
from envault.pin import pin_key
from envault.env_count import count_entries, CountResult

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    vault = {}
    for key, val in [
        ("APP_SECRET", "abc"),
        ("APP_KEY", "xyz"),
        ("DB_HOST", "localhost"),
        ("DB_PORT", "5432"),
        ("REDIS_URL", "redis://localhost"),
    ]:
        vault[key] = encrypt_to_b64(val.encode(), PASSWORD)
    save_vault(path, vault)
    return path


def test_count_total(vault_file):
    result = count_entries(vault_file)
    assert result.total == 5


def test_count_pinned_empty_initially(vault_file):
    result = count_entries(vault_file)
    assert result.pinned == 0


def test_count_pinned_after_pinning(vault_file):
    pin_key(vault_file, "APP_SECRET")
    pin_key(vault_file, "DB_HOST")
    result = count_entries(vault_file)
    assert result.pinned == 2


def test_count_tagged_initially_zero(vault_file):
    result = count_entries(vault_file)
    assert result.tagged == 0
    assert result.by_tag == {}


def test_count_tagged_after_tagging(vault_file):
    add_tag(vault_file, "APP_SECRET", "app")
    add_tag(vault_file, "APP_KEY", "app")
    add_tag(vault_file, "DB_HOST", "db")
    result = count_entries(vault_file)
    assert result.tagged == 3
    assert result.by_tag["app"] == 2
    assert result.by_tag["db"] == 1


def test_count_with_prefix_filter(vault_file):
    result = count_entries(vault_file, prefix="APP_")
    assert result.total == 2


def test_count_with_prefix_filter_db(vault_file):
    result = count_entries(vault_file, prefix="DB_")
    assert result.total == 2


def test_count_group_by_prefix(vault_file):
    result = count_entries(vault_file, group_by_prefix=True)
    assert result.by_prefix["APP"] == 2
    assert result.by_prefix["DB"] == 2
    assert result.by_prefix["REDIS"] == 1


def test_count_str_output(vault_file):
    result = count_entries(vault_file, group_by_prefix=True)
    text = str(result)
    assert "Total entries" in text
    assert "Pinned" in text
    assert "By prefix" in text


def test_count_result_is_dataclass(vault_file):
    result = count_entries(vault_file)
    assert isinstance(result, CountResult)
    assert hasattr(result, "total")
    assert hasattr(result, "by_tag")
