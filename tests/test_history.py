"""Tests for envault.history module."""

import json
import time
import pytest
from envault.history import (
    format_history,
    load_history,
    record_snapshot,
    save_history,
)


@pytest.fixture
def hist_file(tmp_path):
    return str(tmp_path / "test.history")


def test_load_history_missing_file(hist_file):
    assert load_history(hist_file) == []


def test_save_and_load_roundtrip(hist_file):
    entries = [{"timestamp": 1.0, "label": "init", "keys": ["A"], "diff": ""}]
    save_history(entries, hist_file)
    loaded = load_history(hist_file)
    assert loaded == entries


def test_record_snapshot_appends(hist_file):
    record_snapshot("first", ["A", "B"], "  + A=***", hist_file)
    record_snapshot("second", ["A", "B", "C"], "  + C=***", hist_file)
    entries = load_history(hist_file)
    assert len(entries) == 2
    assert entries[0]["label"] == "first"
    assert entries[1]["label"] == "second"
    assert entries[1]["keys"] == ["A", "B", "C"]


def test_record_snapshot_has_timestamp(hist_file):
    before = time.time()
    record_snapshot("ts-test", [], "", hist_file)
    after = time.time()
    entries = load_history(hist_file)
    assert before <= entries[0]["timestamp"] <= after


def test_format_history_empty():
    result = format_history([])
    assert "No history" in result


def test_format_history_shows_label(hist_file):
    record_snapshot("deploy-v1", ["DB_HOST"], "  + DB_HOST=***", hist_file)
    entries = load_history(hist_file)
    result = format_history(entries)
    assert "deploy-v1" in result
    assert "DB_HOST" in result
