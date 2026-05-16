"""Tests for envault.env_reorder."""

import json
import pytest

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64
from envault.env_reorder import reorder_keys, ReorderError

_PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    entries = {
        "ZEBRA": encrypt_to_b64("val1", _PASSWORD),
        "ALPHA": encrypt_to_b64("val2", _PASSWORD),
        "MANGO": encrypt_to_b64("val3", _PASSWORD),
        "BANANA": encrypt_to_b64("val4", _PASSWORD),
    }
    save_vault(path, {"entries": entries})
    return path


def test_reorder_alpha_sorts_keys(vault_file):
    result = reorder_keys(vault_file, mode="alpha")
    assert result.new_order == ["ALPHA", "BANANA", "MANGO", "ZEBRA"]


def test_reorder_alpha_desc_sorts_descending(vault_file):
    result = reorder_keys(vault_file, mode="alpha_desc")
    assert result.new_order == ["ZEBRA", "MANGO", "BANANA", "ALPHA"]


def test_reorder_alpha_persists_to_vault(vault_file):
    reorder_keys(vault_file, mode="alpha")
    vault = load_vault(vault_file)
    assert list(vault["entries"].keys()) == ["ALPHA", "BANANA", "MANGO", "ZEBRA"]


def test_reorder_dry_run_does_not_modify_vault(vault_file):
    original = list(load_vault(vault_file)["entries"].keys())
    reorder_keys(vault_file, mode="alpha", dry_run=True)
    after = list(load_vault(vault_file)["entries"].keys())
    assert after == original


def test_reorder_dry_run_result_has_flag(vault_file):
    result = reorder_keys(vault_file, mode="alpha", dry_run=True)
    assert result.dry_run is True


def test_reorder_explicit_order(vault_file):
    result = reorder_keys(
        vault_file,
        mode="explicit",
        explicit_order=["MANGO", "ZEBRA"],
    )
    # MANGO, ZEBRA first; remaining keys appended
    assert result.new_order[:2] == ["MANGO", "ZEBRA"]
    assert set(result.new_order) == {"ALPHA", "BANANA", "MANGO", "ZEBRA"}


def test_reorder_explicit_unknown_key_raises(vault_file):
    with pytest.raises(ReorderError, match="MISSING"):
        reorder_keys(vault_file, mode="explicit", explicit_order=["MISSING"])


def test_reorder_explicit_without_list_raises(vault_file):
    with pytest.raises(ReorderError, match="explicit_order"):
        reorder_keys(vault_file, mode="explicit")


def test_reorder_unknown_mode_raises(vault_file):
    with pytest.raises(ReorderError, match="Unknown reorder mode"):
        reorder_keys(vault_file, mode="random")


def test_reorder_result_original_order_preserved(vault_file):
    original = list(load_vault(vault_file)["entries"].keys())
    result = reorder_keys(vault_file, mode="alpha")
    assert result.original_order == original


def test_reorder_str_output_contains_keys(vault_file):
    result = reorder_keys(vault_file, mode="alpha")
    text = str(result)
    assert "ALPHA" in text
    assert "ZEBRA" in text


def test_reorder_str_dry_run_label(vault_file):
    result = reorder_keys(vault_file, mode="alpha", dry_run=True)
    assert "dry run" in str(result)
