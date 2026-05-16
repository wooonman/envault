"""Tests for envault.env_annotate."""

import json
import pytest

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64
from envault.env_annotate import (
    AnnotateError,
    AnnotateResult,
    get_annotation,
    set_annotation,
    clear_annotation,
    list_annotations,
    format_annotation_report,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    vault = {
        "API_KEY": encrypt_to_b64("secret123", PASSWORD),
        "DB_URL": encrypt_to_b64("postgres://localhost/db", PASSWORD),
    }
    save_vault(path, vault)
    return path


def test_set_annotation_stores_value(vault_file):
    result = set_annotation(vault_file, "API_KEY", "owner", "team-backend")
    assert result.new_value == "team-backend"
    assert result.old_value is None
    assert result.key == "API_KEY"
    assert result.annotation_key == "owner"


def test_get_annotation_returns_value(vault_file):
    set_annotation(vault_file, "API_KEY", "env", "production")
    val = get_annotation(vault_file, "API_KEY", "env")
    assert val == "production"


def test_get_annotation_missing_returns_none(vault_file):
    val = get_annotation(vault_file, "API_KEY", "nonexistent")
    assert val is None


def test_set_annotation_overwrites_existing(vault_file):
    set_annotation(vault_file, "DB_URL", "tier", "free")
    result = set_annotation(vault_file, "DB_URL", "tier", "paid")
    assert result.old_value == "free"
    assert result.new_value == "paid"


def test_set_annotation_missing_key_raises(vault_file):
    with pytest.raises(AnnotateError, match="not found"):
        set_annotation(vault_file, "GHOST_KEY", "owner", "nobody")


def test_clear_annotation_removes_entry(vault_file):
    set_annotation(vault_file, "API_KEY", "owner", "alice")
    result = clear_annotation(vault_file, "API_KEY", "owner")
    assert result.cleared is True
    assert result.old_value == "alice"
    assert get_annotation(vault_file, "API_KEY", "owner") is None


def test_clear_annotation_nonexistent_is_graceful(vault_file):
    result = clear_annotation(vault_file, "API_KEY", "missing_field")
    assert result.cleared is True
    assert result.old_value is None


def test_list_annotations_returns_all(vault_file):
    set_annotation(vault_file, "API_KEY", "owner", "bob")
    set_annotation(vault_file, "API_KEY", "env", "staging")
    ann = list_annotations(vault_file, "API_KEY")
    assert ann == {"owner": "bob", "env": "staging"}


def test_list_annotations_empty_key(vault_file):
    ann = list_annotations(vault_file, "DB_URL")
    assert ann == {}


def test_format_annotation_report_empty():
    assert format_annotation_report([]) == "No annotations changed."


def test_format_annotation_report_shows_results(vault_file):
    r1 = set_annotation(vault_file, "API_KEY", "owner", "carol")
    r2 = clear_annotation(vault_file, "API_KEY", "owner")
    report = format_annotation_report([r1, r2])
    assert "API_KEY" in report
    assert "carol" in report
    assert "cleared" in report
