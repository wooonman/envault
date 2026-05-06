"""Tests for envault.diff module."""

import pytest
from envault.diff import diff_envs, format_diff, parse_env_lines


ENV_TEXT = """
# a comment
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
"""


def test_parse_env_lines_basic():
    result = parse_env_lines(ENV_TEXT)
    assert result == {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
    }


def test_parse_env_lines_empty():
    assert parse_env_lines("") == {}
    assert parse_env_lines("# only comments\n") == {}


def test_diff_envs_added():
    old = {"A": "1"}
    new = {"A": "1", "B": "2"}
    added, removed, changed = diff_envs(old, new)
    assert added == ["B"]
    assert removed == []
    assert changed == []


def test_diff_envs_removed():
    old = {"A": "1", "B": "2"}
    new = {"A": "1"}
    added, removed, changed = diff_envs(old, new)
    assert added == []
    assert removed == ["B"]
    assert changed == []


def test_diff_envs_changed():
    old = {"A": "1"}
    new = {"A": "2"}
    added, removed, changed = diff_envs(old, new)
    assert changed == ["A"]


def test_format_diff_masks_values():
    old = {"A": "secret"}
    new = {"A": "newsecret", "B": "val"}
    result = format_diff(old, new, mask_values=True)
    assert "secret" not in result
    assert "***" in result


def test_format_diff_no_changes():
    env = {"A": "1"}
    result = format_diff(env, env)
    assert "no changes" in result
