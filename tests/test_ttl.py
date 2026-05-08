"""Tests for envault.ttl module."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from envault.ttl import (
    TTLError,
    clear_expiry,
    format_ttl_report,
    get_ttl_data,
    is_expired,
    purge_expired,
    set_expiry,
)


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    data = {
        "entries": {
            "DB_URL": "encryptedblob1",
            "API_KEY": "encryptedblob2",
            "SECRET": "encryptedblob3",
        }
    }
    path.write_text(json.dumps(data))
    return path


def test_get_ttl_data_empty(vault_file: Path):
    assert get_ttl_data(vault_file) == {}


def test_get_ttl_data_missing_file(tmp_path: Path):
    assert get_ttl_data(tmp_path / "nonexistent.vault") == {}


def test_set_expiry_stores_timestamp(vault_file: Path):
    set_expiry(vault_file, "DB_URL", 3600)
    ttl_data = get_ttl_data(vault_file)
    assert "DB_URL" in ttl_data


def test_set_expiry_missing_key_raises(vault_file: Path):
    with pytest.raises(TTLError, match="not found"):
        set_expiry(vault_file, "MISSING_KEY", 60)


def test_set_expiry_zero_seconds_raises(vault_file: Path):
    with pytest.raises(TTLError, match="positive"):
        set_expiry(vault_file, "DB_URL", 0)


def test_is_expired_no_ttl_returns_false(vault_file: Path):
    assert is_expired(vault_file, "DB_URL") is False


def test_is_expired_future_returns_false(vault_file: Path):
    set_expiry(vault_file, "DB_URL", 9999)
    assert is_expired(vault_file, "DB_URL") is False


def test_is_expired_past_returns_true(vault_file: Path):
    set_expiry(vault_file, "API_KEY", 1)
    time.sleep(1.05)
    assert is_expired(vault_file, "API_KEY") is True


def test_clear_expiry_removes_ttl(vault_file: Path):
    set_expiry(vault_file, "DB_URL", 3600)
    result = clear_expiry(vault_file, "DB_URL")
    assert result is True
    assert "DB_URL" not in get_ttl_data(vault_file)


def test_clear_expiry_no_ttl_returns_false(vault_file: Path):
    result = clear_expiry(vault_file, "DB_URL")
    assert result is False


def test_purge_expired_removes_expired_keys(vault_file: Path):
    set_expiry(vault_file, "API_KEY", 1)
    set_expiry(vault_file, "DB_URL", 9999)
    time.sleep(1.05)
    removed = purge_expired(vault_file)
    assert "API_KEY" in removed
    assert "DB_URL" not in removed
    data = json.loads(vault_file.read_text())
    assert "API_KEY" not in data["entries"]
    assert "DB_URL" in data["entries"]


def test_purge_expired_nothing_to_purge(vault_file: Path):
    removed = purge_expired(vault_file)
    assert removed == []


def test_format_ttl_report_empty():
    report = format_ttl_report({})
    assert "No TTL" in report


def test_format_ttl_report_shows_keys(vault_file: Path):
    set_expiry(vault_file, "SECRET", 3600)
    ttl_data = get_ttl_data(vault_file)
    report = format_ttl_report(ttl_data)
    assert "SECRET" in report
    assert "active" in report
