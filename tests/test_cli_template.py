"""Tests for envault/cli_template.py"""

import argparse
import sys
from unittest.mock import patch

import pytest

from envault.cli_template import cmd_template
from envault.vault import lock


@pytest.fixture()
def vault_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("APP_ENV=production\nSECRET_KEY=s3cr3t\n")
    vf = str(tmp_path / ".envault")
    lock(str(env), vf, "pass")
    return vf


def _args(template, vault, output=None):
    ns = argparse.Namespace(template=template, vault=vault, output=output)
    return ns


def test_cmd_template_stdout(tmp_path, vault_file, capsys):
    tmpl = tmp_path / "t.tmpl"
    tmpl.write_text("env={{APP_ENV}}")

    with patch("envault.cli_template.get_password", return_value="pass"):
        cmd_template(_args(str(tmpl), vault_file))

    captured = capsys.readouterr()
    assert "env=production" in captured.out


def test_cmd_template_writes_file(tmp_path, vault_file):
    tmpl = tmp_path / "t.tmpl"
    tmpl.write_text("key={{SECRET_KEY}}")
    out = tmp_path / "result.txt"

    with patch("envault.cli_template.get_password", return_value="pass"):
        cmd_template(_args(str(tmpl), vault_file, str(out)))

    assert out.read_text() == "key=s3cr3t"


def test_cmd_template_missing_key_exits(tmp_path, vault_file):
    tmpl = tmp_path / "t.tmpl"
    tmpl.write_text("{{DOES_NOT_EXIST}}")

    with patch("envault.cli_template.get_password", return_value="pass"):
        with pytest.raises(SystemExit) as exc_info:
            cmd_template(_args(str(tmpl), vault_file))
    assert exc_info.value.code == 1


def test_cmd_template_missing_template_file_exits(tmp_path, vault_file):
    with patch("envault.cli_template.get_password", return_value="pass"):
        with pytest.raises(SystemExit) as exc_info:
            cmd_template(_args(str(tmp_path / "nope.tmpl"), vault_file))
    assert exc_info.value.code == 1


def test_add_template_subcommand_registers(tmp_path):
    from envault.cli_template import add_template_subcommand

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_template_subcommand(sub)
    args = parser.parse_args(["template", "my.tmpl", "--vault", ".envault"])
    assert args.template == "my.tmpl"
    assert args.vault == ".envault"
    assert args.output is None
