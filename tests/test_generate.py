"""Tests for envault/generate.py"""

import pytest
from envault.generate import (
    generate_secret,
    generate_hex,
    generate_urlsafe,
    generate_for_key,
    format_generate_report,
    GenerateError,
    DEFAULT_LENGTH,
    SPECIAL_CHARS,
)


def test_generate_secret_default_length():
    val = generate_secret()
    assert len(val) == DEFAULT_LENGTH


def test_generate_secret_custom_length():
    val = generate_secret(length=20)
    assert len(val) == 20


def test_generate_secret_too_short_raises():
    with pytest.raises(GenerateError):
        generate_secret(length=4)


def test_generate_secret_with_special_chars():
    # Run many times; at least one should contain a special char
    results = [generate_secret(length=64, use_special=True) for _ in range(20)]
    combined = "".join(results)
    assert any(c in SPECIAL_CHARS for c in combined)


def test_generate_secret_uniqueness():
    a = generate_secret()
    b = generate_secret()
    assert a != b


def test_generate_hex_returns_hex_string():
    val = generate_hex(16)
    assert all(c in "0123456789abcdef" for c in val)


def test_generate_hex_too_short_raises():
    with pytest.raises(GenerateError):
        generate_hex(length=2)


def test_generate_urlsafe_returns_string():
    val = generate_urlsafe(16)
    assert isinstance(val, str)
    assert len(val) > 0


def test_generate_urlsafe_too_short_raises():
    with pytest.raises(GenerateError):
        generate_urlsafe(length=1)


def test_generate_for_key_stores_value(tmp_path):
    from envault.vault import load_vault, unlock

    vault_path = tmp_path / "test.vault"
    vault = load_vault(str(vault_path))
    password = "testpass"

    value = generate_for_key(vault, "MY_SECRET", password)
    vault["path"] = str(vault_path)

    from envault.vault import save_vault
    save_vault(vault)

    decrypted = unlock(vault, "MY_SECRET", password)
    assert decrypted == value


def test_generate_for_key_overwrite_false_raises(tmp_path):
    from envault.vault import load_vault

    vault_path = tmp_path / "test.vault"
    vault = load_vault(str(vault_path))
    password = "testpass"

    generate_for_key(vault, "MY_KEY", password)
    with pytest.raises(GenerateError, match="already exists"):
        generate_for_key(vault, "MY_KEY", password, overwrite=False)


def test_generate_for_key_overwrite_true_replaces(tmp_path):
    from envault.vault import load_vault, unlock

    vault_path = tmp_path / "test.vault"
    vault = load_vault(str(vault_path))
    password = "testpass"

    v1 = generate_for_key(vault, "MY_KEY", password)
    v2 = generate_for_key(vault, "MY_KEY", password, overwrite=True)
    assert unlock(vault, "MY_KEY", password) == v2


def test_generate_for_key_unknown_mode_raises(tmp_path):
    from envault.vault import load_vault

    vault = load_vault(str(tmp_path / "v.vault"))
    with pytest.raises(GenerateError, match="Unknown mode"):
        generate_for_key(vault, "K", "pw", mode="base58")


def test_format_generate_report():
    report = format_generate_report("API_KEY", "abc123", "hex")
    assert "API_KEY" in report
    assert "abc123" in report
    assert "hex" in report
