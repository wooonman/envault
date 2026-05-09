"""Add or update individual key-value entries in the vault."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64


class SetError(Exception):
    pass


@dataclass
class SetResult:
    key: str
    overwritten: bool

    def __str__(self) -> str:
        action = "Updated" if self.overwritten else "Added"
        return f"{action}: {self.key}"


def set_entry(
    vault_path: str,
    key: str,
    value: str,
    password: str,
    *,
    overwrite: bool = True,
) -> SetResult:
    """Encrypt *value* and store it under *key* in the vault.

    Raises SetError if the key already exists and *overwrite* is False.
    """
    if not key:
        raise SetError("Key must not be empty.")
    if "=" in key:
        raise SetError(f"Key must not contain '=': {key!r}")

    vault = load_vault(vault_path)
    entries: dict = vault.setdefault("entries", {})

    already_exists = key in entries
    if already_exists and not overwrite:
        raise SetError(
            f"Key {key!r} already exists. Use overwrite=True to replace it."
        )

    entries[key] = encrypt_to_b64(value, password)
    save_vault(vault_path, vault)
    return SetResult(key=key, overwritten=already_exists)


def set_entries(
    vault_path: str,
    pairs: dict[str, str],
    password: str,
    *,
    overwrite: bool = True,
) -> list[SetResult]:
    """Bulk-set multiple key/value pairs. Returns one SetResult per entry."""
    results = []
    for key, value in pairs.items():
        results.append(
            set_entry(vault_path, key, value, password, overwrite=overwrite)
        )
    return results


def format_set_report(results: list[SetResult]) -> str:
    if not results:
        return "No entries changed."
    return "\n".join(str(r) for r in results)
