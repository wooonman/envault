"""Tests for envault.env_resolve."""

from __future__ import annotations

import json
import pytest

from envault.crypto import encrypt_to_b64
from envault.env_resolve import resolve_references, ResolveResult

PASSWORD = "testpass"


def _make_vault(tmp_path, entries: dict) -> str:
    vault = {k: encrypt_to_b64(v, PASSWORD) for k, v in entries.items()}
    path = tmp_path / "test.vault.json"
    path.write_text(json.dumps(vault))
    return str(path)


@pytest.fixture
def vault_file(tmp_path):
    return _make_vault(
        tmp_path,
        {
            "BASE_URL": "https://example.com",
            "API_URL": "${BASE_URL}/api",
            "FULL_PATH": "${API_URL}/v1",
            "PLAIN": "no-reference-here",
        },
    )


def test_resolve_returns_result_object(vault_file):
    result = resolve_references(vault_file, PASSWORD)
    assert isinstance(result, ResolveResult)


def test_resolve_direct_reference(vault_file):
    result = resolve_references(vault_file, PASSWORD)
    assert result.resolved.get("API_URL") == "https://example.com/api"


def test_resolve_transitive_reference(vault_file):
    result = resolve_references(vault_file, PASSWORD)
    assert result.resolved.get("FULL_PATH") == "https://example.com/api/v1"


def test_plain_key_not_in_resolved(vault_file):
    result = resolve_references(vault_file, PASSWORD)
    assert "PLAIN" not in result.resolved


def test_unresolved_reference(tmp_path):
    path = _make_vault(tmp_path, {"FOO": "${MISSING_KEY}"})
    result = resolve_references(path, PASSWORD)
    assert "FOO" in result.unresolved


def test_cycle_detection(tmp_path):
    path = _make_vault(tmp_path, {"A": "${B}", "B": "${A}"})
    result = resolve_references(path, PASSWORD)
    # at least one of A or B is flagged as a cycle or unresolved
    flagged = set(result.cycles) | set(result.unresolved)
    assert flagged  # something was flagged


def test_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_references(str(tmp_path / "nonexistent.vault.json"), PASSWORD)


def test_str_output_resolved(vault_file):
    result = resolve_references(vault_file, PASSWORD)
    text = str(result)
    assert "Resolved" in text
    assert "API_URL" in text


def test_str_output_no_refs(tmp_path):
    path = _make_vault(tmp_path, {"KEY": "plain-value"})
    result = resolve_references(path, PASSWORD)
    text = str(result)
    assert "No variable references found" in text
