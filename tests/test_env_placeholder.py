"""Tests for envault.env_placeholder."""

import json
import pytest

from envault.env_placeholder import (
    _is_placeholder,
    check_placeholders,
    PlaceholderResult,
)
from envault.vault import save_vault
from envault.crypto import encrypt_to_b64

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")

    def _enc(v):
        return encrypt_to_b64(v, PASSWORD)

    data = {
        "REAL_KEY": {"value": _enc("supersecret123")},
        "CHANGE_ME_KEY": {"value": _enc("CHANGE_ME")},
        "TODO_KEY": {"value": _enc("TODO")},
        "ANGLE_KEY": {"value": _enc("<your-api-key>")},
        "BRACKET_KEY": {"value": _enc("[REPLACE]")},
        "TEMPLATE_KEY": {"value": _enc("${MY_SECRET}")},
        "DUMMY_KEY": {"value": _enc("dummy_value")},
        "EXAMPLE_KEY": {"value": _enc("example-token-abc")},
    }
    with open(path, "w") as f:
        json.dump(data, f)
    return path


# --- unit tests for _is_placeholder ---

@pytest.mark.parametrize("value", [
    "CHANGE_ME", "changeme", "TODO", "todo",
    "<api-key>", "[PLACEHOLDER]", "${SECRET}",
    "***", "PLACEHOLDER", "REPLACE_ME",
    "N/A", "n/a", "DUMMY_VALUE", "example-token",
    "YOUR_SECRET_HERE",
])
def test_is_placeholder_detects_known_patterns(value):
    assert _is_placeholder(value) is not None


@pytest.mark.parametrize("value", [
    "sk-abc123xyz", "postgresql://user:pass@host/db",
    "true", "3600", "production",
])
def test_is_placeholder_ignores_real_values(value):
    assert _is_placeholder(value) is None


# --- integration tests for check_placeholders ---

def test_check_placeholders_returns_result(vault_file):
    result = check_placeholders(vault_file, PASSWORD)
    assert isinstance(result, PlaceholderResult)


def test_check_placeholders_detects_change_me(vault_file):
    result = check_placeholders(vault_file, PASSWORD)
    keys = [e.key for e in result.entries]
    assert "CHANGE_ME_KEY" in keys


def test_check_placeholders_detects_todo(vault_file):
    result = check_placeholders(vault_file, PASSWORD)
    keys = [e.key for e in result.entries]
    assert "TODO_KEY" in keys


def test_check_placeholders_does_not_flag_real_key(vault_file):
    result = check_placeholders(vault_file, PASSWORD)
    keys = [e.key for e in result.entries]
    assert "REAL_KEY" not in keys


def test_check_placeholders_found_flag(vault_file):
    result = check_placeholders(vault_file, PASSWORD)
    assert result.found is True


def test_check_placeholders_str_contains_count(vault_file):
    result = check_placeholders(vault_file, PASSWORD)
    text = str(result)
    assert "placeholder" in text.lower()


def test_check_placeholders_entries_sorted(vault_file):
    result = check_placeholders(vault_file, PASSWORD)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_check_placeholders_empty_vault(tmp_path):
    path = str(tmp_path / "empty.json")
    with open(path, "w") as f:
        json.dump({}, f)
    result = check_placeholders(path, PASSWORD)
    assert not result.found
    assert "No placeholder" in str(result)
