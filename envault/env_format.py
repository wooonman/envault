"""Reformat and normalize vault entries' keys (e.g. uppercase, strip whitespace)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault, save_vault
from envault.crypto import decrypt_from_b64, encrypt_to_b64


class FormatError(Exception):
    pass


@dataclass
class FormatResult:
    renamed: List[tuple] = field(default_factory=list)   # (old_key, new_key)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.renamed:
            lines.append(f"Reformatted {len(self.renamed)} key(s):")
            for old, new in self.renamed:
                lines.append(f"  {old!r} -> {new!r}")
        else:
            lines.append("No keys needed reformatting.")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} key(s) (already normalised or conflict): {', '.join(self.skipped)}")
        return "\n".join(lines)


def _normalize_key(key: str, style: str) -> str:
    key = key.strip()
    if style == "upper":
        return key.upper()
    if style == "lower":
        return key.lower()
    if style == "snake":
        return key.upper().replace("-", "_").replace(" ", "_")
    raise FormatError(f"Unknown style: {style!r}. Choose from: upper, lower, snake")


def format_keys(
    vault_path: str,
    password: str,
    style: str = "upper",
    dry_run: bool = False,
) -> FormatResult:
    """Normalize all entry keys in the vault to the given style."""
    vault = load_vault(vault_path)
    entries: dict = vault.get("entries", {})

    result = FormatResult()
    new_entries: dict = {}

    for key, value in entries.items():
        normalized = _normalize_key(key, style)
        if normalized == key:
            result.skipped.append(key)
            new_entries[key] = value
        elif normalized in entries or normalized in new_entries:
            result.skipped.append(key)
            new_entries[key] = value
        else:
            result.renamed.append((key, normalized))
            new_entries[normalized] = value

    if result.renamed and not dry_run:
        vault["entries"] = new_entries
        save_vault(vault_path, vault)

    return result
