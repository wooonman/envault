"""Tests for envault.cli_lock_status."""

from __future__ import annotations

import argparse
import json
import pytest

from envault.cli_lock_status import cmd_lock_status, add_lock_status_subcommand
from envault.vault import lock


@pytest.fixture()
def vault_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("SECRET=abc123\n")
    path = tmp_path / ".envault"
    lock(str(env), str(path), "pass")
    return str(path)


def _args(vault, fail_unencrypted=False):
    ns = argparse.Namespace(vault=vault, fail_unencrypted=fail_unencrypted)
    return ns


def test_cmd_lock_status_prints_output(vault_file, capsys):
    cmd_lock_status(_args(vault_file))
    out = capsys.readouterr().out
    assert "SECRET" in out


def test_cmd_lock_status_missing_vault_exits(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        cmd_lock_status(_args(str(tmp_path / "nope.vault")))
    assert exc_info.value.code == 1


def test_cmd_lock_status_fail_unencrypted_exits_2(tmp_path, capsys):
    path = tmp_path / "plain.vault"
    path.write_text(json.dumps({"entries": {"KEY": "plaintext"}}))
    with pytest.raises(SystemExit) as exc_info:
        cmd_lock_status(_args(str(path), fail_unencrypted=True))
    assert exc_info.value.code == 2


def test_cmd_lock_status_all_encrypted_no_exit(vault_file):
    # Should NOT raise SystemExit
    cmd_lock_status(_args(vault_file, fail_unencrypted=True))


def test_add_lock_status_subcommand_registers():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_lock_status_subcommand(subparsers)
    args = parser.parse_args(["status", "--vault", ".envault"])
    assert args.vault == ".envault"
    assert hasattr(args, "func")
