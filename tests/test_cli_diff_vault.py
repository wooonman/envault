"""Tests for envault.cli_diff_vault."""

import argparse
import pytest
from unittest.mock import patch

from envault.vault import lock
from envault.cli_diff_vault import cmd_diff_vaults


PASSWORD = "cli-test-pass"


@pytest.fixture()
def vault_a(tmp_path):
    env = tmp_path / "a.env"
    env.write_text("ALPHA=1\nSHARED=x\n")
    v = tmp_path / "a.vault.json"
    lock(str(env), str(v), PASSWORD)
    return str(v)


@pytest.fixture()
def vault_b(tmp_path):
    env = tmp_path / "b.env"
    env.write_text("BETA=2\nSHARED=x\n")
    v = tmp_path / "b.vault.json"
    lock(str(env), str(v), PASSWORD)
    return str(v)


def _args(vault_a, vault_b, same_password=True):
    ns = argparse.Namespace(
        vault_a=vault_a,
        vault_b=vault_b,
        same_password=same_password,
    )
    return ns


def test_cmd_diff_vaults_prints_summary(vault_a, vault_b, capsys):
    with patch("envault.cli_diff_vault.get_password", return_value=PASSWORD):
        cmd_diff_vaults(_args(vault_a, vault_b))
    out = capsys.readouterr().out
    assert "added" in out or "removed" in out


def test_cmd_diff_vaults_identical_says_identical(vault_a, capsys):
    with patch("envault.cli_diff_vault.get_password", return_value=PASSWORD):
        cmd_diff_vaults(_args(vault_a, vault_a))
    out = capsys.readouterr().out
    assert "identical" in out.lower()


def test_cmd_diff_vaults_wrong_password_exits(vault_a, vault_b):
    with patch("envault.cli_diff_vault.get_password", return_value="wrong"):
        with pytest.raises(SystemExit) as exc_info:
            cmd_diff_vaults(_args(vault_a, vault_b))
    assert exc_info.value.code == 1


def test_cmd_diff_vaults_missing_file_exits(vault_a):
    with patch("envault.cli_diff_vault.get_password", return_value=PASSWORD):
        with pytest.raises(SystemExit) as exc_info:
            cmd_diff_vaults(_args(vault_a, "/no/such/file.json"))
    assert exc_info.value.code == 1


def test_cmd_diff_vaults_shows_key_symbols(vault_a, vault_b, capsys):
    with patch("envault.cli_diff_vault.get_password", return_value=PASSWORD):
        cmd_diff_vaults(_args(vault_a, vault_b))
    out = capsys.readouterr().out
    # added (+) and removed (-) keys should appear
    assert "+" in out
    assert "-" in out
