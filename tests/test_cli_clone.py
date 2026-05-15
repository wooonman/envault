"""Tests for envault/cli_clone.py"""

from __future__ import annotations

import argparse
import pytest

from envault.cli_clone import cmd_clone, add_clone_subcommand
from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64


PASSWORD = "clipass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    entries = {
        "API_KEY": encrypt_to_b64(b"abc123", PASSWORD),
        "TOKEN": encrypt_to_b64(b"tok456", PASSWORD),
    }
    save_vault(path, {"entries": entries})
    return path


def _args(vault, src_key, **kwargs):
    ns = argparse.Namespace(
        vault=vault,
        src_key=src_key,
        dest_key=kwargs.get("dest_key", None),
        dest_vault=kwargs.get("dest_vault", None),
        overwrite=kwargs.get("overwrite", False),
    )
    return ns


def test_cmd_clone_same_vault(vault_file, monkeypatch, capsys):
    monkeypatch.setattr("envault.cli_clone.get_password", lambda _: PASSWORD)
    cmd_clone(_args(vault_file, "API_KEY", dest_key="API_KEY_COPY"))
    out = capsys.readouterr().out
    assert "Cloned" in out
    vault = load_vault(vault_file)
    assert "API_KEY_COPY" in vault["entries"]


def test_cmd_clone_missing_key_exits(vault_file, monkeypatch):
    monkeypatch.setattr("envault.cli_clone.get_password", lambda _: PASSWORD)
    with pytest.raises(SystemExit) as exc:
        cmd_clone(_args(vault_file, "NONEXISTENT", dest_key="COPY"))
    assert exc.value.code == 1


def test_cmd_clone_no_overwrite_exits(vault_file, monkeypatch):
    monkeypatch.setattr("envault.cli_clone.get_password", lambda _: PASSWORD)
    with pytest.raises(SystemExit) as exc:
        cmd_clone(_args(vault_file, "API_KEY", dest_key="TOKEN"))
    assert exc.value.code == 1


def test_cmd_clone_with_overwrite(vault_file, monkeypatch, capsys):
    monkeypatch.setattr("envault.cli_clone.get_password", lambda _: PASSWORD)
    cmd_clone(_args(vault_file, "API_KEY", dest_key="TOKEN", overwrite=True))
    vault = load_vault(vault_file)
    decrypted = decrypt_from_b64(vault["entries"]["TOKEN"], PASSWORD)
    assert decrypted == b"abc123"


def test_add_clone_subcommand_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_clone_subcommand(sub)
    args = parser.parse_args(["clone", "my.vault", "MY_KEY"])
    assert args.src_key == "MY_KEY"
    assert args.vault == "my.vault"
    assert args.overwrite is False
