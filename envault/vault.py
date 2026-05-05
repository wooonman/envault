"""Vault file management — read, write, and parse .env.vault files."""

import json
import os
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt_to_b64, decrypt_from_b64

DEFAULT_VAULT_FILE = ".env.vault"


def load_vault(vault_path: str = DEFAULT_VAULT_FILE) -> dict:
    """Load and parse the vault JSON file. Returns empty dict if not found."""
    path = Path(vault_path)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_vault(data: dict, vault_path: str = DEFAULT_VAULT_FILE) -> None:
    """Persist vault data as formatted JSON."""
    with open(vault_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def lock(env_path: str, password: str, vault_path: str = DEFAULT_VAULT_FILE) -> None:
    """Encrypt a .env file and store it in the vault."""
    env_file = Path(env_path)
    if not env_file.exists():
        raise FileNotFoundError(f"{env_path} not found")

    plaintext = env_file.read_text()
    encrypted = encrypt_to_b64(plaintext, password)

    vault = load_vault(vault_path)
    vault[env_path] = {"encrypted": encrypted}
    save_vault(vault, vault_path)


def unlock(env_path: str, password: str, vault_path: str = DEFAULT_VAULT_FILE) -> None:
    """Decrypt a vault entry and write the .env file back to disk."""
    vault = load_vault(vault_path)
    if env_path not in vault:
        raise KeyError(f"No entry for '{env_path}' in vault")

    encrypted = vault[env_path]["encrypted"]
    plaintext = decrypt_from_b64(encrypted, password)
    Path(env_path).write_text(plaintext)
