"""Tests for envault.import_env"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.import_env import (
    parse_dotenv,
    parse_json_env,
    import_entries,
    format_import_report,
)
from envault.vault import lock, unlock

PASSWORD = "test-import-pw"


@pytest.fixture()
def tmp_vault(tmp_path):
    env = tmp_path / ".env"
    env.write_text("EXISTING=hello\nOLD=world\n")
    vault = tmp_path / ".envault"
    lock(env, vault, PASSWORD)
    return vault


# --- parse_dotenv ---

def test_parse_dotenv_basic():
    result = parse_dotenv('KEY=value\nFOO=bar\n')
    assert result == {"KEY": "value", "FOO": "bar"}


def test_parse_dotenv_strips_quotes():
    result = parse_dotenv('SECRET="my secret"\n')
    assert result["SECRET"] == "my secret"


def test_parse_dotenv_ignores_comments():
    result = parse_dotenv('# comment\nA=1\n')
    assert "A" in result
    assert len(result) == 1


def test_parse_dotenv_skips_lines_without_equals():
    result = parse_dotenv('NOEQ\nB=2\n')
    assert list(result.keys()) == ["B"]


# --- parse_json_env ---

def test_parse_json_env_basic():
    text = json.dumps({"X": "1", "Y": "hello"})
    result = parse_json_env(text)
    assert result == {"X": "1", "Y": "hello"}


def test_parse_json_env_non_dict_raises():
    with pytest.raises(ValueError):
        parse_json_env(json.dumps(["a", "b"]))


# --- import_entries ---

def test_import_entries_adds_new_keys(tmp_vault):
    new_entries = {"NEW_KEY": "newval"}
    imported, skipped = import_entries(tmp_vault, PASSWORD, new_entries)
    assert "NEW_KEY" in imported
    assert skipped == []
    result = unlock(tmp_vault, PASSWORD)
    assert result.get("NEW_KEY") == "newval"


def test_import_entries_skips_existing_without_overwrite(tmp_vault):
    entries = {"EXISTING": "changed"}
    imported, skipped = import_entries(tmp_vault, PASSWORD, entries, overwrite=False)
    assert "EXISTING" in skipped
    assert imported == []
    result = unlock(tmp_vault, PASSWORD)
    assert result["EXISTING"] == "hello"


def test_import_entries_overwrites_when_flag_set(tmp_vault):
    entries = {"EXISTING": "updated"}
    imported, skipped = import_entries(tmp_vault, PASSWORD, entries, overwrite=True)
    assert "EXISTING" in imported
    result = unlock(tmp_vault, PASSWORD)
    assert result["EXISTING"] == "updated"


# --- format_import_report ---

def test_format_import_report_shows_imported():
    report = format_import_report(["A", "B"], [])
    assert "Imported" in report
    assert "A" in report


def test_format_import_report_shows_skipped():
    report = format_import_report([], ["C"])
    assert "Skipped" in report


def test_format_import_report_nothing():
    report = format_import_report([], [])
    assert "Nothing" in report
