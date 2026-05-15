"""Tests for envault.cli_bulk_rename."""

from __future__ import annotations

import argparse
import sys
from unittest.mock import patch

import pytest

from envault.vault import lock, load_vault
from envault.cli_bulk_rename import cmd_bulk_rename

PASSWORD = "cli-pass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    lock(path, "OLD_KEY", "value1", PASSWORD)
    lock(path, "OLD_OTHER", "value2", PASSWORD)
    lock(path, "KEEP_KEY", "value3", PASSWORD)
    return path


def _args(**kwargs):
    defaults = {
        "vault": None,
        "from_prefix": None,
        "to_prefix": "",
        "map": None,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_bulk_rename_prefix(vault_file, capsys):
    args = _args(vault=vault_file, from_prefix="OLD_", to_prefix="NEW_")
    with patch("envault.cli_bulk_rename.get_password", return_value=PASSWORD):
        cmd_bulk_rename(args)
    vault = load_vault(vault_file)
    assert "NEW_KEY" in vault
    assert "NEW_OTHER" in vault


def test_cmd_bulk_rename_dry_run_prints_prefix(vault_file, capsys):
    args = _args(vault=vault_file, from_prefix="OLD_", to_prefix="NEW_", dry_run=True)
    with patch("envault.cli_bulk_rename.get_password", return_value=PASSWORD):
        cmd_bulk_rename(args)
    out = capsys.readouterr().out
    assert "dry-run" in out
    # vault unchanged
    vault = load_vault(vault_file)
    assert "OLD_KEY" in vault


def test_cmd_bulk_rename_map(vault_file, capsys):
    args = _args(vault=vault_file, map=["OLD_KEY=RENAMED_KEY"])
    with patch("envault.cli_bulk_rename.get_password", return_value=PASSWORD):
        cmd_bulk_rename(args)
    vault = load_vault(vault_file)
    assert "RENAMED_KEY" in vault
    assert "OLD_KEY" not in vault


def test_cmd_bulk_rename_bad_map_pair_exits(vault_file):
    args = _args(vault=vault_file, map=["NODIVIDER"])
    with patch("envault.cli_bulk_rename.get_password", return_value=PASSWORD):
        with pytest.raises(SystemExit):
            cmd_bulk_rename(args)
