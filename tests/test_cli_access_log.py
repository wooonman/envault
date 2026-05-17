"""Tests for envault.cli_access_log"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envault.vault import save_vault
from envault.crypto import encrypt_to_b64
from envault.cli_access_log import cmd_access_log
from envault.env_access_log import record_access

PASSWORD = "clipass"


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "vault.json"
    vault = {"TOKEN": encrypt_to_b64("abc123", PASSWORD)}
    save_vault(path, vault)
    return path


def _args(vault: Path, subaction: str, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(vault=str(vault), subaction=subaction, **kwargs)


def test_cmd_access_log_record(vault_file: Path, capsys) -> None:
    args = _args(vault_file, "record", key="TOKEN", action="read")
    cmd_access_log(args)
    captured = capsys.readouterr()
    assert "Recorded" in captured.out
    assert "TOKEN" in captured.out


def test_cmd_access_log_list_empty(vault_file: Path, capsys) -> None:
    args = _args(vault_file, "list", key=None, filter_action=None)
    cmd_access_log(args)
    captured = capsys.readouterr()
    assert "No access log entries" in captured.out


def test_cmd_access_log_list_after_record(vault_file: Path, capsys) -> None:
    record_access(vault_file, "TOKEN", "write")
    args = _args(vault_file, "list", key=None, filter_action=None)
    cmd_access_log(args)
    captured = capsys.readouterr()
    assert "TOKEN" in captured.out
    assert "WRITE" in captured.out


def test_cmd_access_log_missing_vault_exits(tmp_path: Path) -> None:
    args = _args(tmp_path / "no.json", "list", key=None, filter_action=None)
    with pytest.raises(SystemExit) as exc:
        cmd_access_log(args)
    assert exc.value.code == 1


def test_cmd_access_log_invalid_action_exits(vault_file: Path) -> None:
    args = _args(vault_file, "record", key="TOKEN", action="peek")
    with pytest.raises(SystemExit) as exc:
        cmd_access_log(args)
    assert exc.value.code == 1
