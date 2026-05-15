"""Vault statistics and summary metrics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envault.lock_unlock_helpers import vault_keys
from envault.vault import load_vault
from envault.pin import get_pins
from envault.tags import get_tags
from envault.ttl import get_ttl_data, is_expired
from envault.notes import _get_notes_map
from envault.description import _get_desc_map


@dataclass
class VaultStats:
    total: int = 0
    pinned: int = 0
    tagged: int = 0
    with_notes: int = 0
    with_description: int = 0
    expired: int = 0
    expiring_soon: int = 0
    tag_counts: Dict[str, int] = field(default_factory=dict)
    keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return format_stats(self)


def compute_stats(vault_path: str, warn_days: int = 7) -> VaultStats:
    """Compute summary statistics for a vault file."""
    vault = load_vault(vault_path)
    entries = {
        k: v for k, v in vault.items() if not k.startswith("__")
    }
    keys = sorted(entries.keys())

    pins = set(get_pins(vault_path))
    notes_map = _get_notes_map(vault)
    desc_map = _get_desc_map(vault)
    ttl_data = get_ttl_data(vault_path)

    tag_counts: Dict[str, int] = {}
    tagged_keys: set = set()

    for key in keys:
        for tag in get_tags(vault_path, key):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            tagged_keys.add(key)

    expired = 0
    expiring_soon = 0
    for key in keys:
        if key in ttl_data:
            if is_expired(vault_path, key):
                expired += 1
            else:
                import datetime
                expiry = ttl_data[key]
                try:
                    dt = datetime.datetime.fromisoformat(expiry)
                    delta = dt - datetime.datetime.now(datetime.timezone.utc)
                    if 0 < delta.total_seconds() <= warn_days * 86400:
                        expiring_soon += 1
                except Exception:
                    pass

    return VaultStats(
        total=len(keys),
        pinned=len([k for k in keys if k in pins]),
        tagged=len(tagged_keys),
        with_notes=len([k for k in keys if notes_map.get(k)]),
        with_description=len([k for k in keys if desc_map.get(k)]),
        expired=expired,
        expiring_soon=expiring_soon,
        tag_counts=tag_counts,
        keys=keys,
    )


def format_stats(stats: VaultStats) -> str:
    lines = [
        f"Total keys      : {stats.total}",
        f"Pinned          : {stats.pinned}",
        f"Tagged          : {stats.tagged}",
        f"With notes      : {stats.with_notes}",
        f"With description: {stats.with_description}",
        f"Expired         : {stats.expired}",
        f"Expiring soon   : {stats.expiring_soon}",
    ]
    if stats.tag_counts:
        lines.append("Tags:")
        for tag, count in sorted(stats.tag_counts.items()):
            lines.append(f"  {tag}: {count}")
    return "\n".join(lines)
