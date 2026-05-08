"""Group management for vault entries."""
from __future__ import annotations

from typing import Dict, List

from envault.vault import load_vault, save_vault


class GroupError(Exception):
    pass


def _get_group_map(vault: dict) -> Dict[str, List[str]]:
    """Return the groups metadata dict (key -> list of group names)."""
    return vault.setdefault("_groups", {})


def get_groups(vault_path: str) -> Dict[str, List[str]]:
    """Return mapping of key -> sorted list of groups."""
    vault = load_vault(vault_path)
    return {k: sorted(v) for k, v in _get_group_map(vault).items()}


def add_to_group(vault_path: str, key: str, group: str) -> None:
    """Add *key* to *group*. Raises GroupError if key not in vault."""
    vault = load_vault(vault_path)
    if key not in vault.get("entries", {}):
        raise GroupError(f"Key '{key}' not found in vault.")
    groups = _get_group_map(vault)
    current = groups.get(key, [])
    if group not in current:
        current = sorted(current + [group])
        groups[key] = current
    save_vault(vault_path, vault)


def remove_from_group(vault_path: str, key: str, group: str) -> None:
    """Remove *key* from *group*. Raises GroupError if not present."""
    vault = load_vault(vault_path)
    groups = _get_group_map(vault)
    current = groups.get(key, [])
    if group not in current:
        raise GroupError(f"Key '{key}' is not in group '{group}'.")
    updated = [g for g in current if g != group]
    if updated:
        groups[key] = updated
    else:
        groups.pop(key, None)
    save_vault(vault_path, vault)


def filter_by_group(vault_path: str, group: str) -> List[str]:
    """Return sorted list of keys that belong to *group*."""
    vault = load_vault(vault_path)
    groups = _get_group_map(vault)
    return sorted(k for k, gs in groups.items() if group in gs)


def format_group_report(key: str, groups: List[str]) -> str:
    """Human-readable summary of groups for a key."""
    if not groups:
        return f"{key}: (no groups)"
    return f"{key}: {', '.join(sorted(groups))}"
