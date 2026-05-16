"""Tests for envault/cli_health.py"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from envault.vault import lock
from envault.cli_health import cmd_health


PASSWORD = "s3cret"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / ".env.vault"
    lock(str(tmp_path / ".env"), str(vf), PASSWORD, env_text="KEY=value\n")
    return vf


def _args(vault: str, fail_on_warning: bool = False) -> SimpleNamespace:
    return SimpleNamespace(vault=vault, fail_on_warning=fail_on_warning)


def test_cmd_health_prints_output(vault_file: Path, capsys) -> None:
    with patch("envault.cli_health.get_password", return_value=PASSWORD):
        cmd_health(_args(str(vault_file)))
    out = capsys.readouterr().out
    assert str(vault_file) in out


def test_cmd_health_missing_vault_exits(tmp_path: Path) -> None:
    with patch("envault.cli_health.get_password", return_value=PASSWORD):
        with pytest.raises(SystemExit) as exc_info:
            cmd_health(_args(str(tmp_path / "missing.vault")))
    assert exc_info.value.code == 1


def test_cmd_health_ok_vault_does_not_exit(vault_file: Path) -> None:
    with patch("envault.cli_health.get_password", return_value=PASSWORD):
        # Should not raise
        cmd_health(_args(str(vault_file)))


def test_cmd_health_fail_on_warning_exits_on_info(vault_file: Path) -> None:
    """With --fail-on-warning, any issue (even info) triggers exit 1."""
    from envault.vault import save_vault
    # wipe vault to produce an 'info: empty' issue
    save_vault(str(vault_file), {})
    with patch("envault.cli_health.get_password", return_value=PASSWORD):
        with pytest.raises(SystemExit) as exc_info:
            cmd_health(_args(str(vault_file), fail_on_warning=True))
    assert exc_info.value.code == 1
