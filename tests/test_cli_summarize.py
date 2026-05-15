"""Tests for envault/cli_summarize.py"""
from __future__ import annotations

import argparse
import json
import sys
import pytest

from envault.lock_unlock_helpers import _make_vault
from envault.cli_summarize import cmd_summarize

PASSWORD = "testpass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    _make_vault(path, PASSWORD, {"ALPHA": "one", "BETA": "two"})
    return path


def _args(vault, json_flag=False):
    ns = argparse.Namespace(vault=vault, json=json_flag)
    return ns


def test_cmd_summarize_prints_output(vault_file, capsys):
    cmd_summarize(_args(vault_file))
    out = capsys.readouterr().out
    assert "Keys" in out
    assert "2" in out


def test_cmd_summarize_includes_vault_path(vault_file, capsys):
    cmd_summarize(_args(vault_file))
    out = capsys.readouterr().out
    assert vault_file in out


def test_cmd_summarize_json_flag_emits_json(vault_file, capsys):
    cmd_summarize(_args(vault_file, json_flag=True))
    out = capsys.readouterr().out
    # JSON block should be present after the text summary
    json_start = out.index("{")
    data = json.loads(out[json_start:])
    assert data["total_keys"] == 2
    assert "vault" in data


def test_cmd_summarize_missing_vault_exits(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        cmd_summarize(_args(str(tmp_path / "missing.vault")))
    assert exc_info.value.code == 1


def test_cmd_summarize_json_has_pinned_key(vault_file, capsys):
    from envault.pin import pin_key
    pin_key(vault_file, "ALPHA")
    cmd_summarize(_args(vault_file, json_flag=True))
    out = capsys.readouterr().out
    json_start = out.index("{")
    data = json.loads(out[json_start:])
    assert "ALPHA" in data["pinned"]
