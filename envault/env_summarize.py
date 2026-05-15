"""Summarize vault contents: key count, tags, pins, expiry, groups, notes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envault.vault import load_vault
from envault.pin import get_pins
from envault.tags import get_tags
from envault.ttl import get_ttl_data
from envault.notes import get_note
from envault.group import get_groups


@dataclass
class VaultSummary:
    vault_path: str
    total_keys: int
    pinned_keys: list[str] = field(default_factory=list)
    tagged_keys: dict[str, list[str]] = field(default_factory=dict)  # tag -> [keys]
    keys_with_expiry: list[str] = field(default_factory=list)
    keys_with_notes: list[str] = field(default_factory=list)
    groups: dict[str, list[str]] = field(default_factory=dict)  # group -> [keys]

    def __str__(self) -> str:
        return format_summary(self)


def summarize_vault(vault_path: str) -> VaultSummary:
    vault = load_vault(vault_path)
    entries = {k: v for k, v in vault.items() if not k.startswith("__")}
    keys = sorted(entries.keys())

    pinned = get_pins(vault_path)
    ttl_data = get_ttl_data(vault_path)
    keys_with_expiry = sorted(k for k in keys if k in ttl_data)
    keys_with_notes = sorted(k for k in keys if get_note(vault_path, k) is not None)
    groups = get_groups(vault_path)

    # build tag -> keys mapping
    tag_map: dict[str, list[str]] = {}
    for key in keys:
        for tag in get_tags(vault_path, key):
            tag_map.setdefault(tag, []).append(key)

    return VaultSummary(
        vault_path=vault_path,
        total_keys=len(keys),
        pinned_keys=pinned,
        tagged_keys=tag_map,
        keys_with_expiry=keys_with_expiry,
        keys_with_notes=keys_with_notes,
        groups=groups,
    )


def format_summary(s: VaultSummary) -> str:
    lines = [
        f"Vault : {s.vault_path}",
        f"Keys  : {s.total_keys}",
        f"Pinned: {len(s.pinned_keys)} ({', '.join(s.pinned_keys) or 'none'})",
        f"Tags  : {len(s.tagged_keys)} unique tag(s)",
    ]
    for tag, keys in sorted(s.tagged_keys.items()):
        lines.append(f"  [{tag}] {', '.join(keys)}")
    lines.append(f"Expiry: {len(s.keys_with_expiry)} key(s) have TTL set")
    lines.append(f"Notes : {len(s.keys_with_notes)} key(s) have notes")
    lines.append(f"Groups: {len(s.groups)} group(s)")
    for grp, keys in sorted(s.groups.items()):
        lines.append(f"  ({grp}) {', '.join(sorted(keys))}")
    return "\n".join(lines)
