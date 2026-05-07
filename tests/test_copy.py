"""Tests for envault/copy.py"""

from __future__ import annotations

import json
import pytest

from envault.copy import copy_key, format_copy_report, CopyError
from envault.vault import lock, unlock


PASSWORD = "test-pass-123"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault.json")
    lock(path, "KEY_A", b"value_a", PASSWORD)
    lock(path, "KEY_B", b"value_b", PASSWORD)
    return path


def test_copy_key_within_same_vault(vault_file):
    report = copy_key(vault_file, "KEY_A", vault_file, "KEY_C", PASSWORD)
    assert report["dst_key"] == "KEY_C"
    assert report["overwritten"] is False
    result = unlock(vault_file, "KEY_C", PASSWORD)
    assert result == b"value_a"


def test_copy_preserves_original(vault_file):
    copy_key(vault_file, "KEY_A", vault_file, "KEY_A_COPY", PASSWORD)
    assert unlock(vault_file, "KEY_A", PASSWORD) == b"value_a"


def test_copy_missing_key_raises(vault_file):
    with pytest.raises(CopyError, match="not found"):
        copy_key(vault_file, "MISSING", vault_file, "KEY_D", PASSWORD)


def test_copy_existing_key_raises_without_overwrite(vault_file):
    with pytest.raises(CopyError, match="already exists"):
        copy_key(vault_file, "KEY_A", vault_file, "KEY_B", PASSWORD)


def test_copy_existing_key_with_overwrite(vault_file):
    report = copy_key(vault_file, "KEY_A", vault_file, "KEY_B", PASSWORD, overwrite=True)
    assert report["overwritten"] is True
    assert unlock(vault_file, "KEY_B", PASSWORD) == b"value_a"


def test_copy_across_vaults(tmp_path):
    src = str(tmp_path / "src.vault.json")
    dst = str(tmp_path / "dst.vault.json")
    lock(src, "MY_KEY", b"secret", PASSWORD)
    lock(dst, "OTHER", b"other", PASSWORD)

    report = copy_key(src, "MY_KEY", dst, "MY_KEY", PASSWORD)
    assert report["src_vault"] == src
    assert report["dst_vault"] == dst
    assert unlock(dst, "MY_KEY", PASSWORD) == b"secret"
    # src unchanged
    assert unlock(src, "MY_KEY", PASSWORD) == b"secret"


def test_format_copy_report_same_vault(vault_file):
    report = copy_key(vault_file, "KEY_A", vault_file, "KEY_COPY", PASSWORD)
    msg = format_copy_report(report)
    assert "KEY_A" in msg
    assert "KEY_COPY" in msg
    assert "same vault" in msg


def test_format_copy_report_overwrite(tmp_path):
    src = str(tmp_path / "v.vault.json")
    lock(src, "X", b"xval", PASSWORD)
    lock(src, "Y", b"yval", PASSWORD)
    report = copy_key(src, "X", src, "Y", PASSWORD, overwrite=True)
    msg = format_copy_report(report)
    assert "Overwrote" in msg
