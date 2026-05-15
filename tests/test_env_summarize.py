"""Tests for envault/env_summarize.py"""
from __future__ import annotations

import json
import pytest

from envault.vault import save_vault
from envault.lock_unlock_helpers import _make_vault
from envault.pin import pin_key
from envault.tags import add_tag
from envault.ttl import set_expiry
from envault.notes import set_note
from envault.group import add_to_group
from envault.env_summarize import summarize_vault, format_summary, VaultSummary

PASSWORD = "testpass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    _make_vault(path, PASSWORD, {"KEY_A": "alpha", "KEY_B": "beta", "KEY_C": "gamma"})
    return path


def test_summarize_returns_vault_summary(vault_file):
    result = summarize_vault(vault_file)
    assert isinstance(result, VaultSummary)


def test_summarize_total_keys(vault_file):
    result = summarize_vault(vault_file)
    assert result.total_keys == 3


def test_summarize_pinned_empty_initially(vault_file):
    result = summarize_vault(vault_file)
    assert result.pinned_keys == []


def test_summarize_pinned_after_pin(vault_file):
    pin_key(vault_file, "KEY_A")
    result = summarize_vault(vault_file)
    assert "KEY_A" in result.pinned_keys


def test_summarize_tags_empty_initially(vault_file):
    result = summarize_vault(vault_file)
    assert result.tagged_keys == {}


def test_summarize_tags_after_tagging(vault_file):
    add_tag(vault_file, "KEY_A", "prod")
    add_tag(vault_file, "KEY_B", "prod")
    result = summarize_vault(vault_file)
    assert "prod" in result.tagged_keys
    assert sorted(result.tagged_keys["prod"]) == ["KEY_A", "KEY_B"]


def test_summarize_expiry_empty_initially(vault_file):
    result = summarize_vault(vault_file)
    assert result.keys_with_expiry == []


def test_summarize_expiry_after_set(vault_file):
    set_expiry(vault_file, "KEY_A", days=30)
    result = summarize_vault(vault_file)
    assert "KEY_A" in result.keys_with_expiry


def test_summarize_notes_empty_initially(vault_file):
    result = summarize_vault(vault_file)
    assert result.keys_with_notes == []


def test_summarize_notes_after_set(vault_file):
    set_note(vault_file, "KEY_B", "important credential")
    result = summarize_vault(vault_file)
    assert "KEY_B" in result.keys_with_notes


def test_summarize_groups_empty_initially(vault_file):
    result = summarize_vault(vault_file)
    assert result.groups == {}


def test_summarize_groups_after_add(vault_file):
    add_to_group(vault_file, "KEY_C", "infra")
    result = summarize_vault(vault_file)
    assert "infra" in result.groups
    assert "KEY_C" in result.groups["infra"]


def test_format_summary_contains_vault_path(vault_file):
    result = summarize_vault(vault_file)
    text = format_summary(result)
    assert vault_file in text


def test_format_summary_contains_key_count(vault_file):
    result = summarize_vault(vault_file)
    text = format_summary(result)
    assert "3" in text


def test_summarize_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        summarize_vault(str(tmp_path / "no_such.vault"))
