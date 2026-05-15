"""Tests for envault/env_archive.py"""

from __future__ import annotations

import json
import pytest

from envault.env_archive import (
    ArchiveError,
    archive_key,
    format_archive_list,
    list_archived,
    restore_key,
)
from envault.vault import lock


@pytest.fixture
def vault_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("ALPHA=hello\nBETA=world\nGAMMA=foo\n")
    vault = tmp_path / ".envault"
    lock(str(env), str(vault), "secret")
    return str(vault)


def test_list_archived_empty(vault_file):
    assert list_archived(vault_file) == []


def test_archive_key_removes_from_entries(vault_file):
    archive_key(vault_file, "ALPHA")
    from envault.vault import load_vault
    v = load_vault(vault_file)
    assert "ALPHA" not in v["entries"]


def test_archive_key_appears_in_list(vault_file):
    archive_key(vault_file, "BETA")
    assert "BETA" in list_archived(vault_file)


def test_archive_key_returns_result(vault_file):
    result = archive_key(vault_file, "GAMMA")
    assert result.key == "GAMMA"
    assert result.action == "archived"
    assert "archived" in str(result)


def test_archive_missing_key_raises(vault_file):
    with pytest.raises(ArchiveError, match="not found"):
        archive_key(vault_file, "MISSING")


def test_restore_key_moves_back_to_entries(vault_file):
    archive_key(vault_file, "ALPHA")
    restore_key(vault_file, "ALPHA")
    from envault.vault import load_vault
    v = load_vault(vault_file)
    assert "ALPHA" in v["entries"]


def test_restore_key_no_longer_in_archive(vault_file):
    archive_key(vault_file, "BETA")
    restore_key(vault_file, "BETA")
    assert "BETA" not in list_archived(vault_file)


def test_restore_missing_archived_key_raises(vault_file):
    with pytest.raises(ArchiveError, match="Archived key not found"):
        restore_key(vault_file, "NOPE")


def test_restore_key_returns_result(vault_file):
    archive_key(vault_file, "GAMMA")
    result = restore_key(vault_file, "GAMMA")
    assert result.key == "GAMMA"
    assert result.action == "restored"


def test_format_archive_list_empty():
    assert format_archive_list([]) == "No archived keys."


def test_format_archive_list_shows_keys():
    out = format_archive_list(["A", "B"])
    assert "A" in out
    assert "B" in out
    assert "Archived keys" in out
