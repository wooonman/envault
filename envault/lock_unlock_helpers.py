"""Internal test/utility helpers for creating pre-populated vaults.

Not part of the public API — used by tests to avoid repeating vault-setup boilerplate.
"""

from __future__ import annotations

from typing import Dict

from envault.vault import lock, load_vault


def _make_vault(path: str, entries: Dict[str, str], password: str) -> str:
    """Create a vault at *path* with the given key/value *entries* encrypted under *password*.

    Returns *path* for convenience.
    """
    for key, value in entries.items():
        lock(path, key, value, password)
    return path


def vault_keys(path: str) -> list[str]:
    """Return the non-meta keys stored in a vault file."""
    vault = load_vault(path)
    return sorted(k for k in vault if not k.startswith("__"))


def vault_has_key(path: str, key: str) -> bool:
    """Return True if *key* exists in the vault (excluding meta keys)."""
    return key in load_vault(path)
