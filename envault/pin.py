"""Pin/unpin specific vault entries to mark them as protected from deletion or overwrite."""

from __future__ import annotations

from typing import Any

VAULT_PINS_KEY = "__pins__"


class PinError(Exception):
    pass


def get_pins(vault: dict[str, Any]) -> list[str]:
    """Return the list of pinned entry names."""
    return list(vault.get(VAULT_PINS_KEY, []))


def pin_key(vault: dict[str, Any], key: str) -> list[str]:
    """Pin an entry. Raises PinError if key does not exist in vault."""
    if key not in vault:
        raise PinError(f"Key '{key}' not found in vault.")
    pins: list[str] = vault.setdefault(VAULT_PINS_KEY, [])
    if key not in pins:
        pins.append(key)
        pins.sort()
    return list(pins)


def unpin_key(vault: dict[str, Any], key: str) -> list[str]:
    """Unpin an entry. Raises PinError if key is not currently pinned."""
    pins: list[str] = vault.get(VAULT_PINS_KEY, [])
    if key not in pins:
        raise PinError(f"Key '{key}' is not pinned.")
    pins.remove(key)
    return list(pins)


def is_pinned(vault: dict[str, Any], key: str) -> bool:
    """Return True if the entry is pinned."""
    return key in vault.get(VAULT_PINS_KEY, [])


def assert_not_pinned(vault: dict[str, Any], key: str, action: str = "modify") -> None:
    """Raise PinError if key is pinned, to guard destructive operations."""
    if is_pinned(vault, key):
        raise PinError(f"Key '{key}' is pinned and cannot be {action}d. Unpin it first.")


def format_pin_report(pins: list[str]) -> str:
    """Return a human-readable list of pinned keys."""
    if not pins:
        return "No entries are currently pinned."
    lines = ["Pinned entries:"]
    for p in pins:
        lines.append(f"  • {p}")
    return "\n".join(lines)
