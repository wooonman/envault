"""Tests for envault/template.py"""

import json
import os
import pytest

from envault.template import (
    render_template,
    list_placeholders,
    format_render_report,
    TemplateError,
)
from envault.vault import lock


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_template_simple():
    result = render_template("Hello, {{NAME}}!", {"NAME": "world"})
    assert result == "Hello, world!"


def test_render_template_multiple_keys():
    tmpl = "{{HOST}}:{{PORT}}"
    result = render_template(tmpl, {"HOST": "localhost", "PORT": "5432"})
    assert result == "localhost:5432"


def test_render_template_repeated_placeholder():
    result = render_template("{{A}} and {{A}}", {"A": "x"})
    assert result == "x and x"


def test_render_template_missing_key_raises():
    with pytest.raises(TemplateError, match="MISSING"):
        render_template("{{MISSING}}", {})


def test_render_template_extra_keys_ignored():
    result = render_template("{{A}}", {"A": "1", "B": "2"})
    assert result == "1"


def test_render_template_whitespace_in_placeholder():
    result = render_template("{{ KEY }}", {"KEY": "val"})
    assert result == "val"


# ---------------------------------------------------------------------------
# list_placeholders
# ---------------------------------------------------------------------------

def test_list_placeholders_returns_sorted_unique():
    tmpl = "{{B}} {{A}} {{B}}"
    assert list_placeholders(tmpl) == ["A", "B"]


def test_list_placeholders_empty():
    assert list_placeholders("no placeholders here") == []


# ---------------------------------------------------------------------------
# format_render_report
# ---------------------------------------------------------------------------

def test_format_render_report_contains_count():
    report = format_render_report("output", ["A", "B"])
    assert "2" in report


def test_format_render_report_lists_keys():
    report = format_render_report("x", ["FOO", "BAR"])
    assert "FOO" in report
    assert "BAR" in report


# ---------------------------------------------------------------------------
# render_template_file integration
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_with_entries(tmp_path):
    vault_file = str(tmp_path / ".envault")
    env_file = str(tmp_path / ".env")
    with open(env_file, "w") as f:
        f.write("DB_HOST=localhost\nDB_PORT=5432\n")
    lock(env_file, vault_file, "secret")
    return vault_file


def test_render_template_file_writes_output(tmp_path, vault_with_entries):
    from envault.template import render_template_file

    tmpl = tmp_path / "app.conf.tmpl"
    tmpl.write_text("host={{DB_HOST}} port={{DB_PORT}}")
    out = tmp_path / "app.conf"

    rendered = render_template_file(
        str(tmpl), vault_with_entries, "secret", str(out)
    )
    assert rendered == "host=localhost port=5432"
    assert out.read_text() == rendered


def test_render_template_file_missing_key_raises(tmp_path, vault_with_entries):
    from envault.template import render_template_file

    tmpl = tmp_path / "bad.tmpl"
    tmpl.write_text("{{NONEXISTENT}}")

    with pytest.raises(TemplateError):
        render_template_file(str(tmpl), vault_with_entries, "secret")
