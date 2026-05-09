"""Tests for envault/notes.py"""

from __future__ import annotations

import json
import pytest

from envault.notes import (
    NoteError,
    clear_note,
    format_notes_report,
    get_note,
    list_notes,
    set_note,
)


@pytest.fixture
def vault_file(tmp_path):
    """A minimal vault with two entries and no notes."""
    path = tmp_path / "test.vault"
    data = {
        "API_KEY": {"ciphertext": "abc"},
        "DB_URL": {"ciphertext": "xyz"},
    }
    path.write_text(json.dumps(data))
    return str(path)


def test_get_note_returns_none_when_absent(vault_file):
    assert get_note(vault_file, "API_KEY") is None


def test_set_note_stores_text(vault_file):
    set_note(vault_file, "API_KEY", "used for payment gateway", password="")
    assert get_note(vault_file, "API_KEY") == "used for payment gateway"


def test_set_note_missing_key_raises(vault_file):
    with pytest.raises(NoteError, match="MISSING"):
        set_note(vault_file, "MISSING", "some note", password="")


def test_set_note_preserves_other_entries(vault_file):
    set_note(vault_file, "API_KEY", "note one", password="")
    set_note(vault_file, "DB_URL", "note two", password="")
    assert get_note(vault_file, "API_KEY") == "note one"
    assert get_note(vault_file, "DB_URL") == "note two"


def test_clear_note_removes_existing(vault_file):
    set_note(vault_file, "API_KEY", "temp note", password="")
    removed = clear_note(vault_file, "API_KEY")
    assert removed is True
    assert get_note(vault_file, "API_KEY") is None


def test_clear_note_returns_false_when_absent(vault_file):
    assert clear_note(vault_file, "API_KEY") is False


def test_list_notes_empty(vault_file):
    assert list_notes(vault_file) == {}


def test_list_notes_returns_all(vault_file):
    set_note(vault_file, "API_KEY", "alpha", password="")
    set_note(vault_file, "DB_URL", "beta", password="")
    result = list_notes(vault_file)
    assert result == {"API_KEY": "alpha", "DB_URL": "beta"}


def test_format_notes_report_empty():
    assert format_notes_report({}) == "No notes found."


def test_format_notes_report_contains_keys():
    report = format_notes_report({"FOO": "bar", "BAZ": "qux"})
    assert "FOO" in report
    assert "bar" in report
    assert "BAZ" in report
