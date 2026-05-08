"""Tests for envault.group."""
from __future__ import annotations

import json
import pytest

from envault.group import (
    GroupError,
    add_to_group,
    filter_by_group,
    format_group_report,
    get_groups,
    remove_from_group,
)


@pytest.fixture()
def vault_file(tmp_path):
    path = tmp_path / "test.envault"
    data = {
        "entries": {
            "DB_HOST": "enc_value_1",
            "DB_PORT": "enc_value_2",
            "API_KEY": "enc_value_3",
        }
    }
    path.write_text(json.dumps(data))
    return str(path)


def test_get_groups_empty(vault_file):
    assert get_groups(vault_file) == {}


def test_add_to_group_stores_entry(vault_file):
    add_to_group(vault_file, "DB_HOST", "database")
    groups = get_groups(vault_file)
    assert "database" in groups["DB_HOST"]


def test_add_to_group_missing_key_raises(vault_file):
    with pytest.raises(GroupError, match="not found"):
        add_to_group(vault_file, "MISSING", "database")


def test_add_to_group_no_duplicates(vault_file):
    add_to_group(vault_file, "DB_HOST", "database")
    add_to_group(vault_file, "DB_HOST", "database")
    groups = get_groups(vault_file)
    assert groups["DB_HOST"].count("database") == 1


def test_add_multiple_groups_sorted(vault_file):
    add_to_group(vault_file, "DB_HOST", "prod")
    add_to_group(vault_file, "DB_HOST", "database")
    groups = get_groups(vault_file)
    assert groups["DB_HOST"] == ["database", "prod"]


def test_remove_from_group(vault_file):
    add_to_group(vault_file, "DB_HOST", "database")
    remove_from_group(vault_file, "DB_HOST", "database")
    groups = get_groups(vault_file)
    assert "DB_HOST" not in groups


def test_remove_from_group_not_present_raises(vault_file):
    with pytest.raises(GroupError, match="not in group"):
        remove_from_group(vault_file, "DB_HOST", "nonexistent")


def test_filter_by_group_returns_matching_keys(vault_file):
    add_to_group(vault_file, "DB_HOST", "database")
    add_to_group(vault_file, "DB_PORT", "database")
    add_to_group(vault_file, "API_KEY", "api")
    result = filter_by_group(vault_file, "database")
    assert result == ["DB_HOST", "DB_PORT"]


def test_filter_by_group_no_match_returns_empty(vault_file):
    assert filter_by_group(vault_file, "nope") == []


def test_format_group_report_with_groups():
    assert format_group_report("DB_HOST", ["database", "prod"]) == "DB_HOST: database, prod"


def test_format_group_report_no_groups():
    assert format_group_report("DB_HOST", []) == "DB_HOST: (no groups)"
