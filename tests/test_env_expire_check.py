"""Tests for envault.env_expire_check."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.vault import lock
from envault.ttl import set_expiry
from envault.env_expire_check import check_expiry, ExpiryEntry


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / "test.vault"
    env = tmp_path / ".env"
    env.write_text("KEY_A=hello\nKEY_B=world\nKEY_C=foo\n")
    lock(str(env), str(vf), PASSWORD)
    return vf


def _future_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _past_iso(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def test_check_expiry_no_ttl_set(vault_file):
    result = check_expiry(str(vault_file))
    assert all(e.days_remaining is None and not e.expired for e in result.entries)
    assert result.expired == []
    assert result.expiring_soon == []


def test_check_expiry_detects_expired_key(vault_file):
    set_expiry(str(vault_file), "KEY_A", _past_iso(1))
    result = check_expiry(str(vault_file))
    expired_keys = [e.key for e in result.expired]
    assert "KEY_A" in expired_keys


def test_check_expiry_detects_expiring_soon(vault_file):
    set_expiry(str(vault_file), "KEY_B", _future_iso(3))
    result = check_expiry(str(vault_file), warn_days=7)
    warn_keys = [e.key for e in result.expiring_soon]
    assert "KEY_B" in warn_keys


def test_check_expiry_far_future_not_flagged(vault_file):
    set_expiry(str(vault_file), "KEY_C", _future_iso(30))
    result = check_expiry(str(vault_file), warn_days=7)
    warn_keys = [e.key for e in result.expiring_soon]
    assert "KEY_C" not in warn_keys


def test_check_expiry_result_str_contains_summary(vault_file):
    text = str(check_expiry(str(vault_file)))
    assert "Total:" in text


def test_expiry_entry_str_expired():
    e = ExpiryEntry(key="X", expires_at="2020-01-01T00:00:00+00:00", expired=True, days_remaining=None)
    assert "EXPIRED" in str(e)


def test_expiry_entry_str_warning():
    e = ExpiryEntry(key="X", expires_at="2099-01-01T00:00:00+00:00", expired=False, days_remaining=3.5)
    assert "WARNING" in str(e)
    assert "3.5" in str(e)


def test_expiry_entry_str_ok():
    e = ExpiryEntry(key="X", expires_at=None, expired=False, days_remaining=None)
    assert "OK" in str(e)


def test_check_expiry_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        check_expiry(str(tmp_path / "nonexistent.vault"))
