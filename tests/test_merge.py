"""Tests for envault.merge."""

import pytest
from envault.merge import merge_envs, format_conflicts


BASE = {"FOO": "1", "BAR": "hello", "SHARED": "same"}
INCOMING = {"BAR": "world", "SHARED": "same", "NEW": "added"}


def test_merge_adds_new_keys():
    merged, _ = merge_envs(BASE, INCOMING, strategy="ours")
    assert merged["NEW"] == "added"


def test_merge_keeps_unchanged_keys():
    merged, _ = merge_envs(BASE, INCOMING, strategy="ours")
    assert merged["FOO"] == "1"
    assert merged["SHARED"] == "same"


def test_merge_ours_keeps_base_on_conflict():
    merged, conflicts = merge_envs(BASE, INCOMING, strategy="ours")
    assert merged["BAR"] == "hello"
    assert len(conflicts) == 1
    assert conflicts[0] == ("BAR", "hello", "world")


def test_merge_theirs_takes_incoming_on_conflict():
    merged, conflicts = merge_envs(BASE, INCOMING, strategy="theirs")
    assert merged["BAR"] == "world"
    assert len(conflicts) == 1


def test_merge_error_raises_on_conflict():
    with pytest.raises(ValueError, match="Merge conflict on key 'BAR'"):
        merge_envs(BASE, INCOMING, strategy="error")


def test_merge_no_conflicts_when_identical():
    a = {"X": "1", "Y": "2"}
    merged, conflicts = merge_envs(a, dict(a), strategy="ours")
    assert conflicts == []
    assert merged == a


def test_merge_empty_incoming():
    merged, conflicts = merge_envs(BASE, {}, strategy="ours")
    assert merged == BASE
    assert conflicts == []


def test_merge_empty_base():
    merged, conflicts = merge_envs({}, INCOMING, strategy="ours")
    assert merged == INCOMING
    assert conflicts == []


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs(BASE, INCOMING, strategy="magic")


def test_format_conflicts_no_conflicts():
    result = format_conflicts([])
    assert result == "No conflicts."


def test_format_conflicts_shows_keys_and_values():
    conflicts = [("BAR", "hello", "world")]
    result = format_conflicts(conflicts)
    assert "BAR" in result
    assert "hello" in result
    assert "world" in result
    assert "Conflicts (1)" in result
