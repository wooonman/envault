"""Tests for envault.env_stats."""
from __future__ import annotations

import json
import pytest

from envault.vault import save_vault
from envault.lock_unlock_helpers import _make_vault
from envault.env_stats import compute_stats, format_stats
from envault.pin import pin_key
from envault.tags import add_tag
from envault.notes import set_note
from envault.description import set_description


PASSWORD = "statspass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = _make_vault(
        {"KEY_A": "alpha", "KEY_B": "beta", "KEY_C": "gamma"},
        PASSWORD,
    )
    save_vault(path, vault)
    return path


def test_compute_stats_total(vault_file):
    stats = compute_stats(vault_file)
    assert stats.total == 3


def test_compute_stats_keys_sorted(vault_file):
    stats = compute_stats(vault_file)
    assert stats.keys == ["KEY_A", "KEY_B", "KEY_C"]


def test_compute_stats_pinned_zero_initially(vault_file):
    stats = compute_stats(vault_file)
    assert stats.pinned == 0


def test_compute_stats_pinned_after_pin(vault_file):
    pin_key(vault_file, "KEY_A")
    stats = compute_stats(vault_file)
    assert stats.pinned == 1


def test_compute_stats_tagged_zero_initially(vault_file):
    stats = compute_stats(vault_file)
    assert stats.tagged == 0
    assert stats.tag_counts == {}


def test_compute_stats_tagged_after_tagging(vault_file):
    add_tag(vault_file, "KEY_A", "production")
    add_tag(vault_file, "KEY_B", "production")
    add_tag(vault_file, "KEY_C", "staging")
    stats = compute_stats(vault_file)
    assert stats.tagged == 3
    assert stats.tag_counts["production"] == 2
    assert stats.tag_counts["staging"] == 1


def test_compute_stats_with_notes(vault_file):
    set_note(vault_file, "KEY_A", "this is a note")
    stats = compute_stats(vault_file)
    assert stats.with_notes == 1


def test_compute_stats_with_description(vault_file):
    set_description(vault_file, "KEY_B", "a description")
    stats = compute_stats(vault_file)
    assert stats.with_description == 1


def test_compute_stats_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        compute_stats(str(tmp_path / "nonexistent.vault"))


def test_format_stats_contains_totals(vault_file):
    stats = compute_stats(vault_file)
    output = format_stats(stats)
    assert "Total keys" in output
    assert "3" in output


def test_format_stats_shows_tag_section(vault_file):
    add_tag(vault_file, "KEY_A", "prod")
    stats = compute_stats(vault_file)
    output = format_stats(stats)
    assert "prod" in output


def test_str_dunder_calls_format(vault_file):
    stats = compute_stats(vault_file)
    assert str(stats) == format_stats(stats)
