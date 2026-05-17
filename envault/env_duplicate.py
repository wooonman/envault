"""Detect duplicate values across vault entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envault.crypto import decrypt_from_b64
from envault.vault import load_vault


@dataclass
class DuplicateGroup:
    value: str
    keys: List[str]

    def __str__(self) -> str:
        keys_str = ", ".join(self.keys)
        return f"[{keys_str}] share the same value"


@dataclass
class DuplicateResult:
    groups: List[DuplicateGroup] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.groups) > 0

    @property
    def total_affected_keys(self) -> int:
        return sum(len(g.keys) for g in self.groups)

    def __str__(self) -> str:
        if not self.has_duplicates:
            return "No duplicate values found."
        lines = [f"{len(self.groups)} duplicate value group(s) found:"]
        for g in self.groups:
            lines.append(f"  {g}")
        return "\n".join(lines)


def find_duplicates(vault_path: str, password: str) -> DuplicateResult:
    """Decrypt all entries and group keys that share identical values."""
    vault = load_vault(vault_path)
    entries = vault.get("entries", {})

    value_map: Dict[str, List[str]] = {}
    for key, ciphertext in entries.items():
        try:
            plaintext = decrypt_from_b64(ciphertext, password)
        except Exception:
            continue
        value_map.setdefault(plaintext, []).append(key)

    groups = [
        DuplicateGroup(value=val, keys=sorted(keys))
        for val, keys in value_map.items()
        if len(keys) > 1
    ]
    groups.sort(key=lambda g: g.keys[0])
    return DuplicateResult(groups=groups)


def format_duplicate_report(result: DuplicateResult) -> str:
    return str(result)
