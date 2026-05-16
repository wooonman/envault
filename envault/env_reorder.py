"""Reorder keys in the vault by sorting them in a specified order."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault, save_vault


class ReorderError(Exception):
    pass


@dataclass
class ReorderResult:
    vault_path: str
    original_order: List[str]
    new_order: List[str]
    dry_run: bool = False

    def __str__(self) -> str:
        tag = " (dry run)" if self.dry_run else ""
        lines = [f"Reordered {len(self.new_order)} keys in '{self.vault_path}'{tag}:"]
        for key in self.new_order:
            lines.append(f"  {key}")
        return "\n".join(lines)


def reorder_keys(
    vault_path: str,
    *,
    mode: str = "alpha",
    explicit_order: Optional[List[str]] = None,
    dry_run: bool = False,
) -> ReorderResult:
    """Reorder vault entry keys.

    mode:
        'alpha'    - alphabetical ascending
        'alpha_desc' - alphabetical descending
        'explicit' - use explicit_order list (unknown keys appended at end)
    """
    vault = load_vault(vault_path)
    entries = vault.get("entries", {})
    original_order = list(entries.keys())

    if mode == "alpha":
        new_keys = sorted(original_order)
    elif mode == "alpha_desc":
        new_keys = sorted(original_order, reverse=True)
    elif mode == "explicit":
        if explicit_order is None:
            raise ReorderError("explicit_order must be provided when mode='explicit'")
        unknown = [k for k in explicit_order if k not in entries]
        if unknown:
            raise ReorderError(f"Keys not found in vault: {', '.join(unknown)}")
        tail = [k for k in original_order if k not in explicit_order]
        new_keys = list(explicit_order) + tail
    else:
        raise ReorderError(f"Unknown reorder mode: '{mode}'")

    reordered = {k: entries[k] for k in new_keys}

    if not dry_run:
        vault["entries"] = reordered
        save_vault(vault_path, vault)

    return ReorderResult(
        vault_path=vault_path,
        original_order=original_order,
        new_order=new_keys,
        dry_run=dry_run,
    )
