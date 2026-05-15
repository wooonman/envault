"""Tests for envault.cli_bulk_export (cmd_bulk_export)."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.cli_bulk_export import cmd_bulk_export
from envault.vault import lock

PASSWORD = "pw"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "v.json"
    lock(path, "DB_URL", "postgres://localhost/db", PASSWORD)
    lock(path, "SECRET", "s3cr3t", PASSWORD)
    return path


def _args(**kwargs) -> argparse.Namespace:
    defaults = dict(vault="", format="dotenv", output=None, tags=[])
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_bulk_export_stdout(vault_file: Path, capsys) -> None:
    args = _args(vault=str(vault_file))
    with patch("envault.cli_bulk_export.get_password", return_value=PASSWORD):
        cmd_bulk_export(args)
    out = capsys.readouterr().out
    assert "DB_URL" in out
    assert "SECRET" in out


def test_cmd_bulk_export_writes_file(vault_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "exported.env"
    args = _args(vault=str(vault_file), output=str(out))
    with patch("envault.cli_bulk_export.get_password", return_value=PASSWORD):
        cmd_bulk_export(args)
    assert out.exists()
    assert "DB_URL" in out.read_text()


def test_cmd_bulk_export_wrong_password_exits(vault_file: Path) -> None:
    args = _args(vault=str(vault_file))
    with patch("envault.cli_bulk_export.get_password", return_value="bad"):
        with pytest.raises(SystemExit) as exc:
            cmd_bulk_export(args)
    assert exc.value.code == 1


def test_cmd_bulk_export_missing_vault_exits(tmp_path: Path) -> None:
    args = _args(vault=str(tmp_path / "nope.json"))
    with patch("envault.cli_bulk_export.get_password", return_value=PASSWORD):
        with pytest.raises(SystemExit) as exc:
            cmd_bulk_export(args)
    assert exc.value.code == 1


def test_cmd_bulk_export_json_format(vault_file: Path, capsys) -> None:
    args = _args(vault=str(vault_file), format="json")
    with patch("envault.cli_bulk_export.get_password", return_value=PASSWORD):
        cmd_bulk_export(args)
    import json
    data = json.loads(capsys.readouterr().out)
    assert "SECRET" in data
