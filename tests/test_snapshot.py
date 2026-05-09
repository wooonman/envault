"""Tests for envault/snapshot.py."""

from __future__ import annotations

import pytest

from envault.snapshot import (
    SnapshotError,
    delete_snapshot,
    format_snapshot_list,
    list_snapshots,
    restore_snapshot,
    save_snapshot,
)


@pytest.fixture
def vault():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
    }


def test_list_snapshots_empty(vault):
    assert list_snapshots(vault) == []


def test_save_snapshot_creates_entry(vault):
    updated = save_snapshot(vault, "v1")
    assert "v1" in list_snapshots(updated)


def test_save_snapshot_captures_entries(vault):
    updated = save_snapshot(vault, "v1")
    snap = updated["__snapshots__"]["v1"]
    assert snap["DB_HOST"] == "localhost"
    assert snap["SECRET_KEY"] == "abc123"


def test_save_snapshot_does_not_include_meta(vault):
    vault["__tags__"] = {"DB_HOST": ["prod"]}
    updated = save_snapshot(vault, "v1")
    snap = updated["__snapshots__"]["v1"]
    assert "__tags__" not in snap


def test_save_snapshot_empty_name_raises(vault):
    with pytest.raises(SnapshotError, match="empty"):
        save_snapshot(vault, "")


def test_save_snapshot_whitespace_name_raises(vault):
    with pytest.raises(SnapshotError):
        save_snapshot(vault, "   ")


def test_restore_snapshot_replaces_entries(vault):
    updated = save_snapshot(vault, "v1")
    updated["DB_HOST"] = "remotehost"
    updated["NEW_KEY"] = "newval"
    restored = restore_snapshot(updated, "v1")
    assert restored["DB_HOST"] == "localhost"
    assert "NEW_KEY" not in restored


def test_restore_snapshot_preserves_meta(vault):
    updated = save_snapshot(vault, "v1")
    updated["__tags__"] = {"DB_HOST": ["prod"]}
    restored = restore_snapshot(updated, "v1")
    assert "__tags__" in restored
    assert "__snapshots__" in restored


def test_restore_snapshot_missing_raises(vault):
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot(vault, "nonexistent")


def test_delete_snapshot_removes_entry(vault):
    updated = save_snapshot(vault, "v1")
    updated = delete_snapshot(updated, "v1")
    assert "v1" not in list_snapshots(updated)


def test_delete_snapshot_missing_raises(vault):
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot(vault, "ghost")


def test_list_snapshots_sorted(vault):
    v = save_snapshot(vault, "beta")
    v = save_snapshot(v, "alpha")
    v = save_snapshot(v, "gamma")
    assert list_snapshots(v) == ["alpha", "beta", "gamma"]


def test_format_snapshot_list_empty():
    assert "No snapshots" in format_snapshot_list([])


def test_format_snapshot_list_shows_names():
    result = format_snapshot_list(["v1", "v2"])
    assert "v1" in result
    assert "v2" in result
