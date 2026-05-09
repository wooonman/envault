"""Per-key human-readable descriptions stored in vault metadata."""

from __future__ import annotations

from typing import Optional

from envault.vault import load_vault, save_vault


class DescriptionError(Exception):
    pass


def _get_desc_map(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("descriptions", {})


def get_description(vault_path: str, key: str) -> Optional[str]:
    """Return the description for *key*, or None if not set."""
    vault = load_vault(vault_path)
    return _get_desc_map(vault).get(key)


def set_description(vault_path: str, key: str, text: str) -> None:
    """Set the description for *key*. Raises DescriptionError if key absent."""
    vault = load_vault(vault_path)
    if key not in vault:
        raise DescriptionError(f"Key '{key}' not found in vault.")
    _get_desc_map(vault)[key] = text
    save_vault(vault_path, vault)


def clear_description(vault_path: str, key: str) -> bool:
    """Remove description for *key*. Returns True if something was removed."""
    vault = load_vault(vault_path)
    desc_map = _get_desc_map(vault)
    if key not in desc_map:
        return False
    del desc_map[key]
    save_vault(vault_path, vault)
    return True


def list_descriptions(vault_path: str) -> dict[str, str]:
    """Return a mapping of key -> description for all keys that have one."""
    vault = load_vault(vault_path)
    return dict(_get_desc_map(vault))


def format_description_report(key: str, text: Optional[str]) -> str:
    if text is None:
        return f"{key}: (no description)"
    return f"{key}: {text}"
