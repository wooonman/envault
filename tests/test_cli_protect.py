"""Tests for envault/cli_protect.py"""

from __future__ import annotations

import argparse
import pytest

from envault.cli_protect import cmd_protect
from envault.env_protect import protect_key
from envault.vault import save_vault


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    save_vault(path, {"API_KEY": "enc_abc", "DB_URL": "enc_def"})
    return path


def _args(vault, key=None, unprotect=False, list_=False):
    ns = argparse.Namespace(vault=vault, key=key, unprotect=unprotect, list=list_)
    return ns


def test_cmd_protect_sets_protection(vault_file, capsys):
    cmd_protect(_args(vault_file, key="API_KEY"))
    out = capsys.readouterr().out
    assert "protected" in out


def test_cmd_protect_list_shows_keys(vault_file, capsys):
    protect_key(vault_file, "API_KEY")
    cmd_protect(_args(vault_file, list_=True))
    out = capsys.readouterr().out
    assert "API_KEY" in out


def test_cmd_protect_list_empty(vault_file, capsys):
    cmd_protect(_args(vault_file, list_=True))
    out = capsys.readouterr().out
    assert "No protected" in out


def test_cmd_protect_unprotect(vault_file, capsys):
    protect_key(vault_file, "DB_URL")
    cmd_protect(_args(vault_file, key="DB_URL", unprotect=True))
    out = capsys.readouterr().out
    assert "no longer protected" in out


def test_cmd_protect_missing_key_exits(vault_file):
    with pytest.raises(SystemExit) as exc:
        cmd_protect(_args(vault_file, key="MISSING"))
    assert exc.value.code == 1


def test_cmd_protect_no_key_no_list_exits(vault_file):
    with pytest.raises(SystemExit) as exc:
        cmd_protect(_args(vault_file, key=None, list_=False))
    assert exc.value.code == 1
