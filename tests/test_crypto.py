"""Tests for envault.crypto encryption/decryption."""

import pytest
from envault.crypto import encrypt, decrypt, encrypt_to_b64, decrypt_from_b64


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DB_HOST=localhost\nDB_PASS=hunter2\nSECRET_KEY=abc123\n"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_decrypt_roundtrip():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(ciphertext, PASSWORD)
    assert recovered == PLAINTEXT


def test_encrypt_produces_different_output_each_call():
    c1 = encrypt(PLAINTEXT, PASSWORD)
    c2 = encrypt(PLAINTEXT, PASSWORD)
    assert c1 != c2  # random salt + nonce each time


def test_decrypt_wrong_password_raises():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(Exception):
        decrypt(ciphertext, "wrong-password")


def test_b64_roundtrip():
    token = encrypt_to_b64(PLAINTEXT, PASSWORD)
    assert isinstance(token, str)
    recovered = decrypt_from_b64(token, PASSWORD)
    assert recovered == PLAINTEXT


def test_b64_wrong_password_raises():
    token = encrypt_to_b64(PLAINTEXT, PASSWORD)
    with pytest.raises(Exception):
        decrypt_from_b64(token, "bad-pass")


def test_empty_string_roundtrip():
    token = encrypt_to_b64("", PASSWORD)
    assert decrypt_from_b64(token, PASSWORD) == ""
