"""Tests for envault.cli_ttl module."""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from envault.cli_ttl import cmd_ttl


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    data = {
        "entries": {
            "DB_URL": "blob1",
            "API_KEY": "blob2",
        }
    }
    path.write_text(json.dumps(data))
    return path


def _args(vault, action, **kwargs):
    return SimpleNamespace(vault=str(vault), ttl_action=action, **kwargs)


def test_cmd_ttl_set(vault_file: Path, capsys):
    args = _args(vault_file, "set", key="DB_URL", seconds=3600)
    cmd_ttl(args)
    out = capsys.readouterr().out
    assert "TTL set" in out
    assert "DB_URL" in out


def test_cmd_ttl_set_missing_key_exits(vault_file: Path, capsys):
    args = _args(vault_file, "set", key="GHOST", seconds=60)
    with pytest.raises(SystemExit):
        cmd_ttl(args)


def test_cmd_ttl_clear_existing(vault_file: Path, capsys):
    set_args = _args(vault_file, "set", key="DB_URL", seconds=3600)
    cmd_ttl(set_args)
    clear_args = _args(vault_file, "clear", key="DB_URL")
    cmd_ttl(clear_args)
    out = capsys.readouterr().out
    assert "cleared" in out


def test_cmd_ttl_clear_no_ttl(vault_file: Path, capsys):
    args = _args(vault_file, "clear", key="DB_URL")
    cmd_ttl(args)
    out = capsys.readouterr().out
    assert "No TTL" in out


def test_cmd_ttl_status_empty(vault_file: Path, capsys):
    args = _args(vault_file, "status")
    cmd_ttl(args)
    out = capsys.readouterr().out
    assert "No TTL" in out


def test_cmd_ttl_status_shows_entry(vault_file: Path, capsys):
    cmd_ttl(_args(vault_file, "set", key="API_KEY", seconds=500))
    capsys.readouterr()
    cmd_ttl(_args(vault_file, "status"))
    out = capsys.readouterr().out
    assert "API_KEY" in out


def test_cmd_ttl_check_no_ttl(vault_file: Path, capsys):
    args = _args(vault_file, "check", key="DB_URL")
    cmd_ttl(args)
    out = capsys.readouterr().out
    assert "no TTL" in out


def test_cmd_ttl_check_expired(vault_file: Path, capsys):
    cmd_ttl(_args(vault_file, "set", key="DB_URL", seconds=1))
    time.sleep(1.05)
    capsys.readouterr()
    cmd_ttl(_args(vault_file, "check", key="DB_URL"))
    out = capsys.readouterr().out
    assert "EXPIRED" in out


def test_cmd_ttl_purge_removes_expired(vault_file: Path, capsys):
    cmd_ttl(_args(vault_file, "set", key="API_KEY", seconds=1))
    time.sleep(1.05)
    capsys.readouterr()
    cmd_ttl(_args(vault_file, "purge"))
    out = capsys.readouterr().out
    assert "Purged" in out
    assert "API_KEY" in out


def test_cmd_ttl_purge_nothing(vault_file: Path, capsys):
    cmd_ttl(_args(vault_file, "purge"))
    out = capsys.readouterr().out
    assert "No expired" in out
