"""Rename or copy keys within the vault."""

from __future__ import annotations

from typing import Optional

from envault.vault import load_vault, save_vault
from envault.crypto import decrypt_from_b64, encrypt_to_b64


class RenameError(Exception):
    pass


def rename_key(
    vault_path: str,
    old_key: str,
    new_key: str,
    password: str,
    *,
    overwrite: bool = False,
    copy: bool = False,
) -> dict:
    """Rename (or copy) *old_key* to *new_key* inside the vault.

    Returns a summary dict with keys: old_key, new_key, action.
    Raises RenameError on bad input or conflicts.
    """
    vault = load_vault(vault_path)

    if old_key not in vault:
        raise RenameError(f"Key '{old_key}' not found in vault.")

    if new_key == old_key:
        raise RenameError("New key name is identical to the old key name.")

    if new_key in vault and not overwrite:
        raise RenameError(
            f"Key '{new_key}' already exists. Use overwrite=True to replace it."
        )

    # Decrypt with old key, re-encrypt under same password for new slot
    plaintext = decrypt_from_b64(vault[old_key]["value"], password)
    vault[new_key] = {"value": encrypt_to_b64(plaintext, password)}

    # Carry over tags if present
    if "tags" in vault[old_key]:
        vault[new_key]["tags"] = list(vault[old_key]["tags"])

    action = "copy" if copy else "rename"
    if not copy:
        del vault[old_key]

    save_vault(vault_path, vault)
    return {"old_key": old_key, "new_key": new_key, "action": action}


def format_rename_report(result: dict) -> str:
    """Human-readable one-liner for a rename/copy result."""
    verb = "Copied" if result["action"] == "copy" else "Renamed"
    return f"{verb} '{result['old_key']}' -> '{result['new_key']}'"
