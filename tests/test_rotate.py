"""Tests for envault.rotate."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from envault.vault import lock
from envault.rotate import rotate_key, rotation_summary


@pytest.fixture()
def tmp_vault(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=secret123\nDB_PASS=hunter2\n")
    vault_file = tmp_path / ".env.vault"
    lock(str(env_file), str(vault_file), "old-pass")
    return str(vault_file)


def test_rotate_key_returns_entry_names(tmp_vault):
    rotated = rotate_key(tmp_vault, "old-pass", "new-pass")
    assert isinstance(rotated, list)
    assert len(rotated) > 0


def test_rotate_key_new_password_works(tmp_vault, tmp_path):
    rotate_key(tmp_vault, "old-pass", "new-pass")

    from envault.vault import unlock

    out_file = tmp_path / ".env.out"
    unlock(tmp_vault, str(out_file), "new-pass")
    content = out_file.read_text()
    assert "API_KEY" in content
    assert "secret123" in content


def test_rotate_key_old_password_no_longer_works(tmp_vault, tmp_path):
    rotate_key(tmp_vault, "old-pass", "new-pass")

    from envault.vault import unlock

    out_file = tmp_path / ".env.out"
    with pytest.raises(Exception):
        unlock(tmp_vault, str(out_file), "old-pass")


def test_rotate_key_wrong_old_password_raises(tmp_vault):
    with pytest.raises(ValueError, match="old password"):
        rotate_key(tmp_vault, "wrong-pass", "new-pass")


def test_rotation_summary_empty():
    assert rotation_summary([]) == "No entries were rotated."


def test_rotation_summary_single():
    result = rotation_summary([".env"])
    assert "1 entry" in result
    assert ".env" in result


def test_rotation_summary_multiple():
    result = rotation_summary([".env", ".env.prod"])
    assert "2 entries" in result
    assert ".env" in result
    assert ".env.prod" in result
