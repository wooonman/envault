"""Retrieve and display entries from the vault."""

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault
from envault.crypto import decrypt_from_b64


class GetError(Exception):
    pass


@dataclass
class GetResult:
    key: str
    value: str
    found: bool = True

    def __str__(self) -> str:
        return self.value if self.found else f"Key '{self.key}' not found."


def get_entry(vault_path: str, key: str, password: str) -> GetResult:
    """Decrypt and return a single entry from the vault."""
    vault = load_vault(vault_path)
    entries = vault.get("entries", {})

    if key not in entries:
        raise GetError(f"Key '{key}' does not exist in the vault.")

    value = decrypt_from_b64(entries[key], password)
    return GetResult(key=key, value=value)


def get_all_entries(vault_path: str, password: str) -> dict[str, str]:
    """Decrypt and return all entries from the vault."""
    vault = load_vault(vault_path)
    entries = vault.get("entries", {})

    result = {}
    for key, ciphertext in entries.items():
        result[key] = decrypt_from_b64(ciphertext, password)
    return result


def format_get_report(results: dict[str, str], reveal: bool = False) -> str:
    """Format a dict of key/value pairs for display."""
    if not results:
        return "(no entries)"
    lines = []
    for key, value in sorted(results.items()):
        display = value if reveal else "*" * min(len(value), 8)
        lines.append(f"{key}={display}")
    return "\n".join(lines)
