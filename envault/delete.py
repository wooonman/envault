"""Delete one or more keys from a vault."""

from __future__ import annotations

from typing import List

from .vault import load_vault, save_vault


class DeleteError(Exception):
    pass


def delete_key(vault_path: str, password: str, key: str) -> dict:
    """Remove *key* from the vault.  Returns the removed entry.

    Raises DeleteError if the key does not exist.
    """
    vault = load_vault(vault_path)
    if key not in vault:
        raise DeleteError(f"Key '{key}' not found in vault.")
    removed = vault.pop(key)
    save_vault(vault_path, vault)
    return removed


def delete_keys(vault_path: str, password: str, keys: List[str]) -> List[str]:
    """Remove multiple keys in a single pass.

    Returns the list of keys that were actually deleted.
    Raises DeleteError if *any* key is missing (no changes are saved).
    """
    vault = load_vault(vault_path)
    missing = [k for k in keys if k not in vault]
    if missing:
        raise DeleteError(
            "Key(s) not found in vault: " + ", ".join(f"'{k}'" for k in missing)
        )
    for k in keys:
        vault.pop(k)
    save_vault(vault_path, vault)
    return list(keys)


def format_delete_report(deleted_keys: List[str]) -> str:
    """Return a human-readable summary of deleted keys."""
    if not deleted_keys:
        return "No keys deleted."
    lines = [f"Deleted {len(deleted_keys)} key(s):"]
    for k in deleted_keys:
        lines.append(f"  - {k}")
    return "\n".join(lines)
