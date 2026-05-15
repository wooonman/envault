"""Tests for envault.cli_grep."""

from __future__ import annotations

import argparse
import pytest
from unittest.mock import patch

from envault.cli_grep import cmd_grep, add_grep_subcommand
from envault.vault import lock


PASSWORD = "clipass"


@pytest.fixture
def vault_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_ENV=production\nSECRET=hunter2\nDEBUG=false\n")
    vault_path = str(tmp_path / "vault.json")
    lock(str(env_file), vault_path, PASSWORD)
    return vault_path


def _args(vault_path, pattern, **kwargs):
    defaults = dict(
        vault=vault_path,
        pattern=pattern,
        keys_only=False,
        ignore_case=False,
        invert=False,
        regex=False,
        line_numbers=False,
        count=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_grep_prints_match(vault_file, capsys):
    with patch("envault.cli_grep.get_password", return_value=PASSWORD):
        cmd_grep(_args(vault_file, "production"))
    out = capsys.readouterr().out
    assert "APP_ENV=production" in out


def test_cmd_grep_no_match_exits_1(vault_file):
    with patch("envault.cli_grep.get_password", return_value=PASSWORD):
        with pytest.raises(SystemExit) as exc_info:
            cmd_grep(_args(vault_file, "ZZZNOMATCH"))
    assert exc_info.value.code == 1


def test_cmd_grep_count_flag(vault_file, capsys):
    with patch("envault.cli_grep.get_password", return_value=PASSWORD):
        cmd_grep(_args(vault_file, "false", count=True))
    out = capsys.readouterr().out
    assert "match" in out


def test_cmd_grep_invalid_regex_exits(vault_file):
    with patch("envault.cli_grep.get_password", return_value=PASSWORD):
        with pytest.raises(SystemExit) as exc_info:
            cmd_grep(_args(vault_file, "[", regex=True))
    assert exc_info.value.code == 1


def test_add_grep_subcommand_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_grep_subcommand(sub)
    args = parser.parse_args(["grep", "vault.json", "pattern"])
    assert args.pattern == "pattern"
    assert args.vault == "vault.json"
