"""Tests for envault.alias."""

from __future__ import annotations

import pytest

from envault.alias import (
    AliasError,
    add_alias,
    format_alias_report,
    get_aliases,
    list_aliases,
    remove_alias,
    resolve_alias,
)


@pytest.fixture()
def vault():
    return {"DB_URL": "enc_abc", "API_KEY": "enc_xyz"}


def test_get_aliases_empty(vault):
    assert get_aliases(vault) == {}


def test_add_alias_stores_mapping(vault):
    updated = add_alias(vault, "db", "DB_URL")
    assert get_aliases(updated) == {"db": "DB_URL"}


def test_add_alias_preserves_vault_entries(vault):
    updated = add_alias(vault, "db", "DB_URL")
    assert "DB_URL" in updated
    assert "API_KEY" in updated


def test_add_alias_duplicate_raises(vault):
    updated = add_alias(vault, "db", "DB_URL")
    with pytest.raises(AliasError, match="already exists"):
        add_alias(updated, "db", "API_KEY")


def test_add_alias_missing_key_raises(vault):
    with pytest.raises(AliasError, match="not found in vault"):
        add_alias(vault, "ghost", "MISSING_KEY")


def test_add_alias_invalid_name_raises(vault):
    with pytest.raises(AliasError, match="Invalid alias name"):
        add_alias(vault, "bad-name!", "DB_URL")


def test_add_alias_clashes_with_vault_key_raises(vault):
    with pytest.raises(AliasError, match="already a vault key"):
        add_alias(vault, "API_KEY", "DB_URL")


def test_remove_alias(vault):
    updated = add_alias(vault, "db", "DB_URL")
    updated = remove_alias(updated, "db")
    assert get_aliases(updated) == {}


def test_remove_alias_missing_raises(vault):
    with pytest.raises(AliasError, match="not found"):
        remove_alias(vault, "nonexistent")


def test_resolve_alias_returns_real_key(vault):
    updated = add_alias(vault, "db", "DB_URL")
    assert resolve_alias(updated, "db") == "DB_URL"


def test_resolve_alias_passthrough_for_non_alias(vault):
    assert resolve_alias(vault, "DB_URL") == "DB_URL"


def test_list_aliases_sorted(vault):
    updated = add_alias(vault, "zkey", "DB_URL")
    updated = add_alias(updated, "akey", "API_KEY")
    assert list_aliases(updated) == ["akey", "zkey"]


def test_format_alias_report_empty(vault):
    report = format_alias_report({})
    assert "No aliases" in report


def test_format_alias_report_shows_mapping(vault):
    aliases = {"db": "DB_URL", "api": "API_KEY"}
    report = format_alias_report(aliases)
    assert "db -> DB_URL" in report
    assert "api -> API_KEY" in report
