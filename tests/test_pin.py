"""Tests for envault.pin."""

from __future__ import annotations

import pytest

from envault.pin import (
    PinError,
    assert_not_pinned,
    format_pin_report,
    get_pins,
    is_pinned,
    pin_key,
    unpin_key,
)


@pytest.fixture()
def vault() -> dict:
    return {"DB_URL": "enc:abc", "SECRET": "enc:xyz", "PORT": "enc:123"}


def test_get_pins_empty(vault):
    assert get_pins(vault) == []


def test_pin_key_adds_to_pins(vault):
    pins = pin_key(vault, "DB_URL")
    assert "DB_URL" in pins


def test_pin_key_is_sorted(vault):
    pin_key(vault, "SECRET")
    pins = pin_key(vault, "DB_URL")
    assert pins == sorted(pins)


def test_pin_key_idempotent(vault):
    pin_key(vault, "DB_URL")
    pins = pin_key(vault, "DB_URL")
    assert pins.count("DB_URL") == 1


def test_pin_key_missing_raises(vault):
    with pytest.raises(PinError, match="not found"):
        pin_key(vault, "NONEXISTENT")


def test_unpin_key_removes_pin(vault):
    pin_key(vault, "SECRET")
    pins = unpin_key(vault, "SECRET")
    assert "SECRET" not in pins


def test_unpin_key_not_pinned_raises(vault):
    with pytest.raises(PinError, match="not pinned"):
        unpin_key(vault, "DB_URL")


def test_is_pinned_true(vault):
    pin_key(vault, "PORT")
    assert is_pinned(vault, "PORT") is True


def test_is_pinned_false(vault):
    assert is_pinned(vault, "PORT") is False


def test_assert_not_pinned_raises_when_pinned(vault):
    pin_key(vault, "SECRET")
    with pytest.raises(PinError, match="pinned"):
        assert_not_pinned(vault, "SECRET", action="delete")


def test_assert_not_pinned_passes_when_not_pinned(vault):
    assert_not_pinned(vault, "DB_URL")  # should not raise


def test_format_pin_report_empty():
    report = format_pin_report([])
    assert "No entries" in report


def test_format_pin_report_lists_keys():
    report = format_pin_report(["DB_URL", "SECRET"])
    assert "DB_URL" in report
    assert "SECRET" in report
    assert "Pinned entries" in report
