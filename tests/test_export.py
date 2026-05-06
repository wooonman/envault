"""Tests for envault.export module."""

import json
import pytest

from envault.export import (
    to_dotenv,
    to_json,
    to_shell_export,
    export_entries,
)


SAMPLE = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "s3cr3t",
    "APP_NAME": "my app",
}


def test_to_dotenv_simple_values():
    result = to_dotenv({"FOO": "bar", "BAZ": "qux"})
    assert "FOO=bar" in result
    assert "BAZ=qux" in result


def test_to_dotenv_quotes_values_with_spaces():
    result = to_dotenv({"APP_NAME": "my app"})
    assert 'APP_NAME="my app"' in result


def test_to_dotenv_ends_with_newline():
    result = to_dotenv({"X": "1"})
    assert result.endswith("\n")


def test_to_dotenv_empty():
    assert to_dotenv({}) == ""


def test_to_json_is_valid_json():
    result = to_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed["SECRET_KEY"] == "s3cr3t"
    assert parsed["APP_NAME"] == "my app"


def test_to_json_sorted_keys():
    result = to_json({"Z": "1", "A": "2"})
    parsed = json.loads(result)
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_to_shell_export_format():
    result = to_shell_export({"FOO": "bar"})
    assert "export FOO='bar'" in result


def test_to_shell_export_escapes_single_quotes():
    result = to_shell_export({"MSG": "it's alive"})
    assert "export MSG='it'\\''s alive'" in result


def test_export_entries_dotenv():
    result = export_entries({"KEY": "val"}, "dotenv")
    assert "KEY=val" in result


def test_export_entries_json():
    result = export_entries({"KEY": "val"}, "json")
    assert json.loads(result)["KEY"] == "val"


def test_export_entries_shell():
    result = export_entries({"KEY": "val"}, "shell")
    assert "export KEY='val'" in result


def test_export_entries_unknown_format_raises():
    with pytest.raises(ValueError, match="Unknown export format"):
        export_entries({"KEY": "val"}, "xml")
