"""Tests for envault.env_check."""

import json
import pytest

from envault.crypto import encrypt_to_b64
from envault.env_check import check_entries, format_check_report, CheckResult


PASSWORD = "testpass"


@pytest.fixture()
def vault_file(tmp_path):
    """Vault with keys: DB_HOST, DB_PORT, SECRET_KEY."""
    data = {}
    for key, val in [("DB_HOST", "localhost"), ("DB_PORT", "5432"), ("SECRET_KEY", "abc")]:
        data[key] = encrypt_to_b64(val.encode(), PASSWORD)
    path = tmp_path / "vault.json"
    path.write_text(json.dumps(data))
    return str(path)


def test_all_expected_keys_present(vault_file):
    result = check_entries(vault_file, ["DB_HOST", "DB_PORT", "SECRET_KEY"])
    assert result.ok
    assert result.missing == []
    assert result.matched == ["DB_HOST", "DB_PORT", "SECRET_KEY"]


def test_missing_key_detected(vault_file):
    result = check_entries(vault_file, ["DB_HOST", "MISSING_KEY"])
    assert not result.ok
    assert "MISSING_KEY" in result.missing
    assert "DB_HOST" in result.matched


def test_extra_keys_ignored_without_strict(vault_file):
    result = check_entries(vault_file, ["DB_HOST"], strict=False)
    assert result.ok
    assert result.extra == []


def test_extra_keys_flagged_with_strict(vault_file):
    result = check_entries(vault_file, ["DB_HOST"], strict=True)
    assert not result.ok
    assert "DB_PORT" in result.extra
    assert "SECRET_KEY" in result.extra


def test_empty_expected_list_strict_flags_all(vault_file):
    result = check_entries(vault_file, [], strict=True)
    assert set(result.extra) == {"DB_HOST", "DB_PORT", "SECRET_KEY"}


def test_meta_keys_excluded(tmp_path):
    """Keys starting with __ should not appear in vault_keys."""
    data = {"__meta": "ignored", "REAL_KEY": encrypt_to_b64(b"val", PASSWORD)}
    path = tmp_path / "vault.json"
    path.write_text(json.dumps(data))
    result = check_entries(str(path), ["REAL_KEY"], strict=True)
    assert result.ok
    assert "__meta" not in result.extra


def test_format_check_report_ok():
    result = CheckResult(matched=["A", "B"], missing=[], extra=[])
    report = format_check_report(result)
    assert "ok" in report
    assert "2 matched" in report


def test_format_check_report_missing():
    result = CheckResult(matched=["A"], missing=["B"], extra=[])
    report = format_check_report(result)
    assert "MISS" in report
    assert "1 missing" in report


def test_format_check_report_strict_extra():
    result = CheckResult(matched=["A"], missing=[], extra=["C"])
    report = format_check_report(result, strict=True)
    assert "XTRA" in report
    assert "1 extra" in report
