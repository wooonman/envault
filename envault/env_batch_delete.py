"""Batch delete multiple keys from a vault."""

from dataclasses import dataclass, field
from typing import List, Optional
from envault.vault import load_vault, save_vault


class BatchDeleteError(Exception):
    pass


@dataclass
class BatchDeleteResult:
    deleted: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.deleted:
            lines.append(f"Deleted ({len(self.deleted)}): {', '.join(self.deleted)}")
        if self.missing:
            lines.append(f"Not found ({len(self.missing)}): {', '.join(self.missing)}")
        if self.skipped:
            lines.append(f"Skipped/pinned ({len(self.skipped)}): {', '.join(self.skipped)}")
        return "\n".join(lines) if lines else "Nothing to delete."


def batch_delete(
    vault_path: str,
    keys: List[str],
    *,
    skip_missing: bool = False,
    skip_pinned: bool = True,
) -> BatchDeleteResult:
    """Delete multiple keys from the vault in one operation."""
    vault = load_vault(vault_path)
    entries = vault.get("entries", {})
    pins = set(vault.get("_pins", []))
    result = BatchDeleteResult()

    for key in keys:
        if key not in entries:
            if skip_missing:
                result.missing.append(key)
                continue
            raise BatchDeleteError(f"Key not found: {key!r}")
        if skip_pinned and key in pins:
            result.skipped.append(key)
            continue
        del entries[key]
        result.deleted.append(key)

    vault["entries"] = entries
    save_vault(vault_path, vault)
    return result


def format_batch_delete_report(result: BatchDeleteResult) -> str:
    return str(result)
