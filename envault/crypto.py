"""Core encryption/decryption utilities for envault using AES-GCM via cryptography library."""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend

SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # AES-256


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a password using scrypt."""
    kdf = Scrypt(
        salt=salt,
        length=KEY_SIZE,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())


def encrypt(plaintext: str, password: str) -> bytes:
    """Encrypt plaintext string and return raw bytes (salt + nonce + ciphertext)."""
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return salt + nonce + ciphertext


def decrypt(data: bytes, password: str) -> str:
    """Decrypt raw bytes back to plaintext string."""
    salt = data[:SALT_SIZE]
    nonce = data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = data[SALT_SIZE + NONCE_SIZE:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode()


def encrypt_to_b64(plaintext: str, password: str) -> str:
    """Encrypt and return base64-encoded string for safe storage."""
    return base64.b64encode(encrypt(plaintext, password)).decode()


def decrypt_from_b64(b64_data: str, password: str) -> str:
    """Decrypt a base64-encoded encrypted string."""
    return decrypt(base64.b64decode(b64_data), password)
