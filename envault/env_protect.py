"""Protect/unprotect keys from accidental modification or deletion."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envault.vault import load_vault, save_vault


class ProtectError(Exception):
    pass


def _get_protected(vault: dict) -> List[str]:
    return sorted(vault.get("__meta__", {}).get("protected", []))


def _set_protected(vault: dict, keys: List[str]) -> None:
    vault.setdefault("__meta__", {})["protected"] = sorted(set(keys))


def get_protected(vault_path: str) -> List[str]:
    """Return all currently protected key names."""
    vault = load_vault(vault_path)
    return _get_protected(vault)


def protect_key(vault_path: str, key: str) -> None:
    """Mark a key as protected."""
    vault = load_vault(vault_path)
    if key not in vault:
        raise ProtectError(f"Key '{key}' not found in vault.")
    protected = _get_protected(vault)
    if key not in protected:
        protected.append(key)
        _set_protected(vault, protected)
        save_vault(vault_path, vault)


def unprotect_key(vault_path: str, key: str) -> None:
    """Remove protection from a key."""
    vault = load_vault(vault_path)
    protected = _get_protected(vault)
    if key not in protected:
        raise ProtectError(f"Key '{key}' is not protected.")
    protected.remove(key)
    _set_protected(vault, protected)
    save_vault(vault_path, vault)


def is_protected(vault_path: str, key: str) -> bool:
    """Return True if the key is currently protected."""
    vault = load_vault(vault_path)
    return key in _get_protected(vault)


def assert_not_protected(vault_path: str, key: str, operation: str = "modify") -> None:
    """Raise ProtectError if the key is protected."""
    if is_protected(vault_path, key):
        raise ProtectError(
            f"Key '{key}' is protected and cannot be {operation}d. "
            "Use 'envault protect --unprotect' to remove protection first."
        )


def format_protect_report(keys: List[str]) -> str:
    if not keys:
        return "No protected keys."
    lines = ["Protected keys:"]
    for k in sorted(keys):
        lines.append(f"  🔒 {k}")
    return "\n".join(lines)
