"""Tests for envault/env_list.py"""

import json
import pytest
from pathlib import Path
from envault.vault import lock
from envault.tags import add_tag
from envault.description import set_description
from envault.pin import pin_key
from envault.env_list import list_entries, format_list, ListEntry


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / ".envault"
    env = tmp_path / ".env"
    env.write_text("DB_URL=postgres://localhost\nSECRET_KEY=abc123\nAPI_TOKEN=tok\n")
    lock(str(env), str(path), PASSWORD)
    return str(path)


def test_list_entries_returns_all_keys(vault_file):
    entries = list_entries(vault_file)
    keys = [e.key for e in entries]
    assert "DB_URL" in keys
    assert "SECRET_KEY" in keys
    assert "API_TOKEN" in keys


def test_list_entries_sorted(vault_file):
    entries = list_entries(vault_file)
    keys = [e.key for e in entries]
    assert keys == sorted(keys)


def test_list_entries_filter_by_tag(vault_file):
    vault = json.loads(Path(vault_file).read_text())
    add_tag(vault, "DB_URL", "database")
    Path(vault_file).write_text(json.dumps(vault))

    entries = list_entries(vault_file, tag_filter="database")
    assert len(entries) == 1
    assert entries[0].key == "DB_URL"


def test_list_entries_pinned_only(vault_file):
    vault = json.loads(Path(vault_file).read_text())
    pin_key(vault, "SECRET_KEY")
    Path(vault_file).write_text(json.dumps(vault))

    entries = list_entries(vault_file, pinned_only=True)
    assert all(e.pinned for e in entries)
    assert any(e.key == "SECRET_KEY" for e in entries)


def test_list_entry_str_with_description(vault_file):
    vault = json.loads(Path(vault_file).read_text())
    set_description(vault, "API_TOKEN", "auth token")
    Path(vault_file).write_text(json.dumps(vault))

    entries = list_entries(vault_file)
    entry = next(e for e in entries if e.key == "API_TOKEN")
    assert "auth token" in str(entry)


def test_format_list_non_verbose(vault_file):
    entries = list_entries(vault_file)
    output = format_list(entries, verbose=False)
    for e in entries:
        assert e.key in output
    assert "tags=" not in output


def test_format_list_verbose(vault_file):
    vault = json.loads(Path(vault_file).read_text())
    add_tag(vault, "DB_URL", "db")
    Path(vault_file).write_text(json.dumps(vault))

    entries = list_entries(vault_file)
    output = format_list(entries, verbose=True)
    assert "tags=db" in output


def test_format_list_empty():
    assert format_list([]) == "(no entries)"


def test_list_entries_missing_vault_raises():
    with pytest.raises(FileNotFoundError):
        list_entries("/nonexistent/.envault")
