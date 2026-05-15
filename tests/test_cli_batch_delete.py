"""CLI-level tests for the batch-delete subcommand."""

import argparse
import pytest
from envault.lock_unlock_helpers import _make_vault
from envault.vault import load_vault, save_vault
from envault.cli_batch_delete import cmd_batch_delete

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    _make_vault(path, {"FOO": "foo", "BAR": "bar", "BAZ": "baz"}, PASSWORD)
    return path


def _args(vault, keys, *, skip_missing=False, force_pinned=False, fail_on_missing=False):
    ns = argparse.Namespace(
        vault=vault,
        keys=keys,
        skip_missing=skip_missing,
        force_pinned=force_pinned,
        fail_on_missing=fail_on_missing,
    )
    return ns


def test_cmd_batch_delete_removes_keys(vault_file, capsys):
    cmd_batch_delete(_args(vault_file, ["FOO", "BAR"]))
    out = capsys.readouterr().out
    assert "FOO" in out or "Deleted" in out
    vault = load_vault(vault_file)
    assert "FOO" not in vault["entries"]
    assert "BAR" not in vault["entries"]


def test_cmd_batch_delete_no_keys_exits(vault_file):
    with pytest.raises(SystemExit) as exc:
        cmd_batch_delete(_args(vault_file, []))
    assert exc.value.code == 1


def test_cmd_batch_delete_missing_key_exits(vault_file):
    with pytest.raises(SystemExit) as exc:
        cmd_batch_delete(_args(vault_file, ["MISSING"]))
    assert exc.value.code == 1


def test_cmd_batch_delete_skip_missing_succeeds(vault_file, capsys):
    cmd_batch_delete(_args(vault_file, ["FOO", "MISSING"], skip_missing=True))
    out = capsys.readouterr().out
    assert "MISSING" in out or "Not found" in out


def test_cmd_batch_delete_fail_on_missing_exits_2(vault_file):
    with pytest.raises(SystemExit) as exc:
        cmd_batch_delete(
            _args(vault_file, ["FOO", "NOPE"], skip_missing=True, fail_on_missing=True)
        )
    assert exc.value.code == 2
