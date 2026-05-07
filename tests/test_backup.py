"""Tests for envault.backup module."""

import json
import os
import pytest
from pathlib import Path

from envault.backup import (
    backup_vault,
    list_backups,
    restore_vault,
    format_backup_list,
)


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / "vault.json"
    p.write_text(json.dumps({"entries": {"KEY": "val"}}))
    return p


@pytest.fixture
def backup_dir(tmp_path):
    d = tmp_path / "backups"
    return d


def test_backup_creates_file(vault_file, backup_dir):
    path = backup_vault(str(vault_file), str(backup_dir))
    assert Path(path).exists()


def test_backup_file_is_named_with_timestamp(vault_file, backup_dir):
    path = backup_vault(str(vault_file), str(backup_dir))
    name = Path(path).name
    assert name.startswith("vault.")
    assert name.endswith(".json")


def test_backup_content_matches_original(vault_file, backup_dir):
    path = backup_vault(str(vault_file), str(backup_dir))
    original = vault_file.read_text()
    backup = Path(path).read_text()
    assert original == backup


def test_backup_missing_vault_raises(backup_dir):
    with pytest.raises(FileNotFoundError):
        backup_vault("/nonexistent/vault.json", str(backup_dir))


def test_list_backups_empty_dir(backup_dir):
    entries = list_backups(str(backup_dir))
    assert entries == []


def test_list_backups_returns_entries(vault_file, backup_dir):
    backup_vault(str(vault_file), str(backup_dir))
    backup_vault(str(vault_file), str(backup_dir))
    entries = list_backups(str(backup_dir))
    assert len(entries) == 2
    assert all("name" in e and "size" in e and "mtime" in e for e in entries)


def test_list_backups_sorted_newest_first(vault_file, backup_dir):
    backup_vault(str(vault_file), str(backup_dir))
    backup_vault(str(vault_file), str(backup_dir))
    entries = list_backups(str(backup_dir))
    names = [e["name"] for e in entries]
    assert names == sorted(names, reverse=True)


def test_restore_vault(vault_file, backup_dir, tmp_path):
    backup_path = backup_vault(str(vault_file), str(backup_dir))
    target = tmp_path / "restored.json"
    restore_vault(backup_path, str(target))
    assert target.exists()
    assert target.read_text() == vault_file.read_text()


def test_restore_no_overwrite_raises(vault_file, backup_dir):
    backup_path = backup_vault(str(vault_file), str(backup_dir))
    with pytest.raises(FileExistsError):
        restore_vault(backup_path, str(vault_file), overwrite=False)


def test_restore_with_overwrite(vault_file, backup_dir):
    backup_path = backup_vault(str(vault_file), str(backup_dir))
    restore_vault(backup_path, str(vault_file), overwrite=True)
    assert vault_file.exists()


def test_format_backup_list_empty():
    result = format_backup_list([])
    assert "No backups" in result


def test_format_backup_list_shows_names():
    entries = [{"name": "vault.20240101T000000Z.json", "size": 128, "mtime": "2024-01-01T00:00:00+00:00"}]
    result = format_backup_list(entries)
    assert "vault.20240101T000000Z.json" in result
    assert "128" in result
