"""Tests for envault/description.py."""

from __future__ import annotations

import json
import pytest

from envault.description import (
    DescriptionError,
    clear_description,
    format_description_report,
    get_description,
    list_descriptions,
    set_description,
)
from envault.vault import lock


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    lock(path, "KEY", "value", "secret")
    lock(path, "OTHER", "other_value", "secret")
    return path


def test_get_description_returns_none_when_absent(vault_file):
    assert get_description(vault_file, "KEY") is None


def test_set_description_stores_text(vault_file):
    set_description(vault_file, "KEY", "The primary API key")
    assert get_description(vault_file, "KEY") == "The primary API key"


def test_set_description_missing_key_raises(vault_file):
    with pytest.raises(DescriptionError, match="MISSING"):
        set_description(vault_file, "MISSING", "should fail")


def test_set_description_preserves_other_entries(vault_file):
    set_description(vault_file, "KEY", "desc")
    assert get_description(vault_file, "OTHER") is None


def test_set_description_overwrite(vault_file):
    set_description(vault_file, "KEY", "first")
    set_description(vault_file, "KEY", "second")
    assert get_description(vault_file, "KEY") == "second"


def test_clear_description_returns_true_when_removed(vault_file):
    set_description(vault_file, "KEY", "to remove")
    assert clear_description(vault_file, "KEY") is True
    assert get_description(vault_file, "KEY") is None


def test_clear_description_returns_false_when_absent(vault_file):
    assert clear_description(vault_file, "KEY") is False


def test_list_descriptions_empty(vault_file):
    assert list_descriptions(vault_file) == {}


def test_list_descriptions_returns_all(vault_file):
    set_description(vault_file, "KEY", "alpha")
    set_description(vault_file, "OTHER", "beta")
    result = list_descriptions(vault_file)
    assert result == {"KEY": "alpha", "OTHER": "beta"}


def test_format_description_report_with_text():
    assert format_description_report("KEY", "some text") == "KEY: some text"


def test_format_description_report_none():
    assert format_description_report("KEY", None) == "KEY: (no description)"
