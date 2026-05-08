"""Key aliasing: map short names to full vault key names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

ALIAS_KEY = "_aliases"


class AliasError(Exception):
    pass


def _get_alias_map(vault: dict) -> Dict[str, str]:
    """Return the alias map stored inside the vault dict."""
    return vault.get(ALIAS_KEY, {})


def get_aliases(vault: dict) -> Dict[str, str]:
    """Return a copy of all aliases {alias: real_key}."""
    return dict(_get_alias_map(vault))


def add_alias(vault: dict, alias: str, key: str) -> dict:
    """Add *alias* pointing to *key*. Raises AliasError if alias already exists."""
    if not alias or not alias.isidentifier():
        raise AliasError(f"Invalid alias name: {alias!r}")
    if key not in vault:
        raise AliasError(f"Key {key!r} not found in vault")
    aliases = _get_alias_map(vault)
    if alias in aliases:
        raise AliasError(f"Alias {alias!r} already exists (points to {aliases[alias]!r})")
    if alias in vault:
        raise AliasError(f"{alias!r} is already a vault key")
    vault = {**vault, ALIAS_KEY: {**aliases, alias: key}}
    return vault


def remove_alias(vault: dict, alias: str) -> dict:
    """Remove *alias*. Raises AliasError if it does not exist."""
    aliases = _get_alias_map(vault)
    if alias not in aliases:
        raise AliasError(f"Alias {alias!r} not found")
    new_aliases = {k: v for k, v in aliases.items() if k != alias}
    vault = {**vault, ALIAS_KEY: new_aliases}
    return vault


def resolve_alias(vault: dict, name: str) -> str:
    """Return the real key for *name*, resolving alias if necessary."""
    aliases = _get_alias_map(vault)
    return aliases.get(name, name)


def list_aliases(vault: dict) -> List[str]:
    """Return sorted list of alias names."""
    return sorted(_get_alias_map(vault).keys())


def format_alias_report(aliases: Dict[str, str]) -> str:
    if not aliases:
        return "No aliases defined."
    lines = [f"  {alias} -> {key}" for alias, key in sorted(aliases.items())]
    return "Aliases:\n" + "\n".join(lines)
