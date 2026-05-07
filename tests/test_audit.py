"""Tests for envault.audit."""

from __future__ import annotations

import json
import pytest

from envault.audit import (
    load_audit,
    save_audit,
    record_event,
    format_audit_log,
    DEFAULT_AUDIT_FILE,
)


@pytest.fixture
def audit_file(tmp_path):
    return str(tmp_path / "audit.json")


def test_load_audit_missing_file(audit_file):
    entries = load_audit(audit_file)
    assert entries == []


def test_save_and_load_roundtrip(audit_file):
    data = [{"timestamp": "2024-01-01T00:00:00+00:00", "action": "lock", "user": "alice", "details": {}}]
    save_audit(data, audit_file)
    loaded = load_audit(audit_file)
    assert loaded == data


def test_record_event_appends(audit_file):
    record_event("lock", {"vault": ".envault"}, audit_path=audit_file, user="bob")
    record_event("unlock", {"vault": ".envault"}, audit_path=audit_file, user="bob")
    entries = load_audit(audit_file)
    assert len(entries) == 2
    assert entries[0]["action"] == "lock"
    assert entries[1]["action"] == "unlock"


def test_record_event_has_timestamp(audit_file):
    event = record_event("rotate", audit_path=audit_file, user="carol")
    assert "timestamp" in event
    assert "T" in event["timestamp"]  # ISO format


def test_record_event_stores_user(audit_file):
    event = record_event("lock", audit_path=audit_file, user="dave")
    assert event["user"] == "dave"


def test_record_event_stores_details(audit_file):
    event = record_event("lock", details={"entries": 3}, audit_path=audit_file, user="eve")
    assert event["details"]["entries"] == 3


def test_format_audit_log_empty():
    result = format_audit_log([])
    assert "No audit" in result


def test_format_audit_log_contains_action(audit_file):
    record_event("lock", audit_path=audit_file, user="frank")
    entries = load_audit(audit_file)
    output = format_audit_log(entries)
    assert "lock" in output
    assert "frank" in output


def test_format_audit_log_shows_details(audit_file):
    record_event("unlock", details={"file": ".env"}, audit_path=audit_file, user="grace")
    entries = load_audit(audit_file)
    output = format_audit_log(entries)
    assert "file=.env" in output
