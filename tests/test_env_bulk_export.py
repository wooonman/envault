"""Tests for envault.env_bulk_export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_bulk_export import BulkExportError, bulk_export
from envault.vault import lock, load_vault, save_vault

PASSWORD = "test-pass"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.json"
    lock(path, "KEY_A", "alpha", PASSWORD)
    lock(path, "KEY_B", "beta", PASSWORD)
    lock(path, "KEY_C", "gamma", PASSWORD)
    return path


def test_bulk_export_returns_result(vault_file: Path) -> None:
    result = bulk_export(vault_file, PASSWORD, fmt="dotenv")
    assert result.fmt == "dotenv"
    assert set(result.keys_exported) == {"KEY_A", "KEY_B", "KEY_C"}


def test_bulk_export_dotenv_content(vault_file: Path) -> None:
    result = bulk_export(vault_file, PASSWORD, fmt="dotenv")
    assert "KEY_A=" in result.content
    assert "alpha" in result.content


def test_bulk_export_json_content(vault_file: Path) -> None:
    result = bulk_export(vault_file, PASSWORD, fmt="json")
    data = json.loads(result.content)
    assert data["KEY_B"] == "beta"


def test_bulk_export_writes_to_file(vault_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.env"
    result = bulk_export(vault_file, PASSWORD, fmt="dotenv", output_path=out)
    assert out.exists()
    assert result.path == out
    assert "KEY_C" in out.read_text()


def test_bulk_export_str_shows_count(vault_file: Path) -> None:
    result = bulk_export(vault_file, PASSWORD)
    assert "3 key(s)" in str(result)


def test_bulk_export_unsupported_format_raises(vault_file: Path) -> None:
    with pytest.raises(BulkExportError, match="Unsupported format"):
        bulk_export(vault_file, PASSWORD, fmt="xml")


def test_bulk_export_wrong_password_raises(vault_file: Path) -> None:
    with pytest.raises(BulkExportError, match="Failed to decrypt"):
        bulk_export(vault_file, "wrong-password")


def test_bulk_export_filter_by_tag(vault_file: Path) -> None:
    vault = load_vault(vault_file)
    vault.setdefault("tags", {})["KEY_A"] = ["prod"]
    vault["tags"]["KEY_C"] = ["prod"]
    save_vault(vault_file, vault)

    result = bulk_export(vault_file, PASSWORD, tags=["prod"])
    assert set(result.keys_exported) == {"KEY_A", "KEY_C"}
    assert "KEY_B" not in result.content


def test_bulk_export_missing_vault_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        bulk_export(tmp_path / "ghost.json", PASSWORD)
