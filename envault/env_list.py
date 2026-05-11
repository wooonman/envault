"""List and display vault entries with optional filtering and metadata."""

from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault
from envault.tags import get_tags
from envault.description import get_description
from envault.pin import is_pinned
from envault.ttl import get_ttl_data, is_expired


@dataclass
class ListEntry:
    key: str
    tags: list = field(default_factory=list)
    description: Optional[str] = None
    pinned: bool = False
    expired: bool = False

    def __str__(self) -> str:
        parts = [self.key]
        if self.pinned:
            parts.append("[pinned]")
        if self.expired:
            parts.append("[expired]")
        if self.tags:
            parts.append(f"tags={','.join(self.tags)}")
        if self.description:
            parts.append(f"# {self.description}")
        return "  ".join(parts)


def list_entries(
    vault_path: str,
    tag_filter: Optional[str] = None,
    pinned_only: bool = False,
    include_expired: bool = True,
) -> list[ListEntry]:
    """Return a sorted list of vault entry metadata."""
    vault = load_vault(vault_path)
    entries = [
        k for k in vault.keys() if not k.startswith("__")
    ]

    results = []
    for key in sorted(entries):
        tags = get_tags(vault, key)
        if tag_filter and tag_filter not in tags:
            continue
        pinned = is_pinned(vault, key)
        if pinned_only and not pinned:
            continue
        desc = get_description(vault, key)
        ttl_data = get_ttl_data(vault_path, key)
        expired = bool(ttl_data) and is_expired(ttl_data)
        if not include_expired and expired:
            continue
        results.append(ListEntry(
            key=key,
            tags=tags,
            description=desc,
            pinned=pinned,
            expired=expired,
        ))

    return results


def format_list(entries: list[ListEntry], verbose: bool = False) -> str:
    """Format a list of entries for display."""
    if not entries:
        return "(no entries)"
    if verbose:
        return "\n".join(str(e) for e in entries)
    return "\n".join(e.key for e in entries)
