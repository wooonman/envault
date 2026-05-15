"""Bulk rename keys in a vault using a prefix swap or explicit mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault
from envault.rename import rename_key, RenameError


@dataclass
class BulkRenameResult:
    renamed: List[tuple] = field(default_factory=list)   # [(old, new), ...]
    skipped: List[tuple] = field(default_factory=list)   # [(old, reason), ...]

    def __str__(self) -> str:
        lines = []
        for old, new in self.renamed:
            lines.append(f"  renamed: {old} -> {new}")
        for old, reason in self.skipped:
            lines.append(f"  skipped: {old} ({reason})")
        return "\n".join(lines) if lines else "  (nothing to do)"


class BulkRenameError(Exception):
    pass


def bulk_rename_prefix(
    vault_path: str,
    password: str,
    old_prefix: str,
    new_prefix: str,
    dry_run: bool = False,
) -> BulkRenameResult:
    """Rename all keys that start with *old_prefix* by replacing it with *new_prefix*."""
    vault = load_vault(vault_path)
    entries = {k: v for k, v in vault.items() if not k.startswith("__")}
    result = BulkRenameResult()

    candidates = [k for k in entries if k.startswith(old_prefix)]
    if not candidates:
        return result

    for old_key in sorted(candidates):
        new_key = new_prefix + old_key[len(old_prefix):]
        if new_key in entries and new_key != old_key:
            result.skipped.append((old_key, f"target '{new_key}' already exists"))
            continue
        if not dry_run:
            try:
                rename_key(vault_path, password, old_key, new_key)
                # reload after each rename so subsequent renames see updated vault
                vault = load_vault(vault_path)
                entries = {k: v for k, v in vault.items() if not k.startswith("__")}
            except RenameError as exc:
                result.skipped.append((old_key, str(exc)))
                continue
        result.renamed.append((old_key, new_key))

    return result


def bulk_rename_map(
    vault_path: str,
    password: str,
    mapping: Dict[str, str],
    dry_run: bool = False,
) -> BulkRenameResult:
    """Rename keys according to an explicit {old: new} mapping."""
    result = BulkRenameResult()

    for old_key, new_key in mapping.items():
        if not dry_run:
            try:
                rename_key(vault_path, password, old_key, new_key)
            except RenameError as exc:
                result.skipped.append((old_key, str(exc)))
                continue
        result.renamed.append((old_key, new_key))

    return result
