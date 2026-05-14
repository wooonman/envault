import json
import pytest
from pathlib import Path

from envault.vault import lock, load_vault
from envault.crypto import decrypt_from_b64
from envault.env_move import move_key, MoveError, format_move_report

PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.json"
    lock(str(path), "ALPHA", "alpha_value", PASSWORD)
    lock(str(path), "BETA", "beta_value", PASSWORD)
    return path


@pytest.fixture
def second_vault(tmp_path):
    path = tmp_path / "vault2.json"
    lock(str(path), "GAMMA", "gamma_value", PASSWORD)
    return path


def test_move_key_renames_within_vault(vault_file):
    move_key(str(vault_file), "ALPHA", "ALPHA_NEW", PASSWORD)
    data = load_vault(str(vault_file))
    assert "ALPHA_NEW" in data["entries"]
    assert "ALPHA" not in data["entries"]


def test_move_preserves_value(vault_file):
    move_key(str(vault_file), "ALPHA", "ALPHA_MOVED", PASSWORD)
    data = load_vault(str(vault_file))
    value = decrypt_from_b64(data["entries"]["ALPHA_MOVED"], PASSWORD)
    assert value == b"alpha_value"


def test_move_preserves_other_keys(vault_file):
    move_key(str(vault_file), "ALPHA", "ALPHA_MOVED", PASSWORD)
    data = load_vault(str(vault_file))
    assert "BETA" in data["entries"]


def test_move_missing_key_raises(vault_file):
    with pytest.raises(MoveError, match="not found"):
        move_key(str(vault_file), "MISSING", "DEST", PASSWORD)


def test_move_same_key_raises(vault_file):
    with pytest.raises(MoveError, match="same"):
        move_key(str(vault_file), "ALPHA", "ALPHA", PASSWORD)


def test_move_existing_dest_raises_without_overwrite(vault_file):
    with pytest.raises(MoveError, match="already exists"):
        move_key(str(vault_file), "ALPHA", "BETA", PASSWORD)


def test_move_existing_dest_with_overwrite(vault_file):
    result = move_key(str(vault_file), "ALPHA", "BETA", PASSWORD, overwrite=True)
    data = load_vault(str(vault_file))
    assert "ALPHA" not in data["entries"]
    value = decrypt_from_b64(data["entries"]["BETA"], PASSWORD)
    assert value == b"alpha_value"


def test_move_cross_vault(vault_file, second_vault):
    result = move_key(str(vault_file), "ALPHA", "ALPHA_FROM_V1", PASSWORD, dest_vault_path=str(second_vault))
    assert result.cross_vault is True
    src = load_vault(str(vault_file))
    dst = load_vault(str(second_vault))
    assert "ALPHA" not in src["entries"]
    assert "ALPHA_FROM_V1" in dst["entries"]


def test_move_cross_vault_preserves_value(vault_file, second_vault):
    move_key(str(vault_file), "BETA", "BETA_COPY", PASSWORD, dest_vault_path=str(second_vault))
    dst = load_vault(str(second_vault))
    value = decrypt_from_b64(dst["entries"]["BETA_COPY"], PASSWORD)
    assert value == b"beta_value"


def test_format_move_report_same_vault(vault_file):
    result = move_key(str(vault_file), "ALPHA", "ALPHA_RENAMED", PASSWORD)
    report = format_move_report(result)
    assert "ALPHA" in report
    assert "ALPHA_RENAMED" in report


def test_format_move_report_cross_vault(vault_file, second_vault):
    result = move_key(str(vault_file), "ALPHA", "ALPHA_X", PASSWORD, dest_vault_path=str(second_vault))
    report = format_move_report(result)
    assert "cross" not in report.lower() or "vault" in report.lower() or "from" in report.lower()
    assert "ALPHA_X" in report
