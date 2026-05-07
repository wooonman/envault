"""Tests for envault.tags module."""

from __future__ import annotations

import pytest

from envault.tags import (
    TAGS_KEY,
    get_tags,
    set_tags,
    add_tag,
    remove_tag,
    filter_by_tag,
    all_tags,
    format_tags_report,
)


@pytest.fixture()
def vault():
    return {"DB_URL": "enc1", "API_KEY": "enc2", "SECRET": "enc3"}


def test_get_tags_empty(vault):
    assert get_tags(vault, "DB_URL") == []


def test_set_tags_stores_sorted(vault):
    set_tags(vault, "DB_URL", ["prod", "backend", "prod"])
    assert vault[TAGS_KEY]["DB_URL"] == ["backend", "prod"]


def test_add_tag_creates_entry(vault):
    add_tag(vault, "API_KEY", "external")
    assert "external" in get_tags(vault, "API_KEY")


def test_add_tag_no_duplicates(vault):
    add_tag(vault, "API_KEY", "external")
    add_tag(vault, "API_KEY", "external")
    assert get_tags(vault, "API_KEY").count("external") == 1


def test_remove_tag_removes_existing(vault):
    add_tag(vault, "SECRET", "sensitive")
    remove_tag(vault, "SECRET", "sensitive")
    assert "sensitive" not in get_tags(vault, "SECRET")


def test_remove_tag_noop_when_missing(vault):
    # should not raise
    remove_tag(vault, "SECRET", "nonexistent")
    assert get_tags(vault, "SECRET") == []


def test_filter_by_tag_returns_matching(vault):
    add_tag(vault, "DB_URL", "prod")
    add_tag(vault, "API_KEY", "prod")
    add_tag(vault, "SECRET", "dev")
    result = filter_by_tag(vault, "prod")
    assert set(result) == {"DB_URL", "API_KEY"}


def test_filter_by_tag_no_match(vault):
    assert filter_by_tag(vault, "staging") == []


def test_all_tags_empty(vault):
    assert all_tags(vault) == {}


def test_all_tags_returns_mapping(vault):
    add_tag(vault, "DB_URL", "prod")
    add_tag(vault, "API_KEY", "external")
    result = all_tags(vault)
    assert "DB_URL" in result
    assert "API_KEY" in result


def test_format_tags_report_no_tags(vault):
    report = format_tags_report(vault)
    assert "No tags" in report


def test_format_tags_report_with_tags(vault):
    add_tag(vault, "DB_URL", "prod")
    report = format_tags_report(vault)
    assert "DB_URL" in report
    assert "prod" in report
