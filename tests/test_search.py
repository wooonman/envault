"""Tests for envault.search."""

from __future__ import annotations

import pytest

from envault.vault import lock
from envault.search import (
    format_search_results,
    search_keys,
    search_values,
)


PASSWORD = "hunter2"

SAMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "DATABASE_POOL": "5",
    "SECRET_KEY": "supersecret",
    "DEBUG": "true",
    "API_ENDPOINT": "https://api.example.com",
}


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / ".env.vault")
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(f"{k}={v}" for k, v in SAMPLE_ENV.items())
    )
    lock(str(env_path), path, PASSWORD)
    return path


def test_search_keys_glob_prefix(vault_file):
    results = search_keys(vault_file, PASSWORD, "DATABASE_*")
    keys = [k for k, _ in results]
    assert "DATABASE_URL" in keys
    assert "DATABASE_POOL" in keys
    assert "SECRET_KEY" not in keys


def test_search_keys_exact_glob(vault_file):
    results = search_keys(vault_file, PASSWORD, "DEBUG")
    assert len(results) == 1
    assert results[0][0] == "DEBUG"


def test_search_keys_regex(vault_file):
    results = search_keys(vault_file, PASSWORD, r"^(SECRET|DEBUG)$", use_glob=False)
    keys = [k for k, _ in results]
    assert "SECRET_KEY" in keys
    assert "DEBUG" in keys
    assert "DATABASE_URL" not in keys


def test_search_keys_no_match(vault_file):
    results = search_keys(vault_file, PASSWORD, "NONEXISTENT_*")
    assert results == []


def test_search_values_substring(vault_file):
    results = search_values(vault_file, PASSWORD, "postgres")
    keys = [k for k, _ in results]
    assert "DATABASE_URL" in keys


def test_search_values_case_insensitive(vault_file):
    results = search_values(vault_file, PASSWORD, "POSTGRES", case_sensitive=False)
    keys = [k for k, _ in results]
    assert "DATABASE_URL" in keys


def test_search_values_case_sensitive_no_match(vault_file):
    results = search_values(vault_file, PASSWORD, "POSTGRES", case_sensitive=True)
    assert results == []


def test_format_search_results_masked():
    results = [("KEY", "mysecret")]
    output = format_search_results(results, reveal=False)
    assert "KEY" in output
    assert "mysecret" not in output
    assert "*" in output


def test_format_search_results_revealed():
    results = [("KEY", "mysecret")]
    output = format_search_results(results, reveal=True)
    assert "mysecret" in output


def test_format_search_results_empty():
    output = format_search_results([])
    assert "No matches" in output
