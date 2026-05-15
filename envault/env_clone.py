"""Clone a vault entry to a new key, optionally across vaults."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.crypto import decrypt_from_b64, encrypt_to_b64


class CloneError(Exception):
    pass


@dataclass
class CloneResult:
    source_key: str
    dest_key: str
    source_vault: str
    dest_vault: str
    overwritten: bool

    def __str__(self) -> str:
        arrow = f"{self.source_vault}:{self.source_key} -> {self.dest_vault}:{self.dest_key}"
        note = " (overwritten)" if self.overwritten else ""
        return f"Cloned {arrow}{note}"


def clone_key(
    src_vault_path: str,
    src_key: str,
    dest_vault_path: str,
    dest_key: str,
    password: str,
    dest_password: Optional[str] = None,
    overwrite: bool = False,
) -> CloneResult:
    """Clone src_key from src_vault into dest_vault as dest_key.

    If dest_vault is the same file as src_vault, dest_password is ignored.
    Re-encrypts the value with dest_password (or password if not given).
    """
    if dest_password is None:
        dest_password = password

    src_vault = load_vault(src_vault_path)
    entries = src_vault.get("entries", {})

    if src_key not in entries:
        raise CloneError(f"Source key '{src_key}' not found in {src_vault_path}")

    # Decrypt value with source password
    raw_value = decrypt_from_b64(entries[src_key], password)

    # Load destination vault (may be same file)
    dest_vault = load_vault(dest_vault_path)
    dest_entries = dest_vault.setdefault("entries", {})

    overwritten = dest_key in dest_entries
    if overwritten and not overwrite:
        raise CloneError(
            f"Destination key '{dest_key}' already exists in {dest_vault_path}. "
            "Use overwrite=True to replace it."
        )

    dest_entries[dest_key] = encrypt_to_b64(raw_value, dest_password)
    save_vault(dest_vault_path, dest_vault)

    return CloneResult(
        source_key=src_key,
        dest_key=dest_key,
        source_vault=src_vault_path,
        dest_vault=dest_vault_path,
        overwritten=overwritten,
    )


def format_clone_report(result: CloneResult) -> str:
    return str(result)
