"""Tag-based grouping and filtering of vault entries."""

from __future__ import annotations

from typing import Dict, List, Optional


TAGS_KEY = "__tags__"


def get_tags(vault: dict, entry: str) -> List[str]:
    """Return the list of tags for a given vault entry."""
    meta = vault.get(TAGS_KEY, {})
    return list(meta.get(entry, []))


def set_tags(vault: dict, entry: str, tags: List[str]) -> dict:
    """Set tags for a vault entry, returning the updated vault."""
    if TAGS_KEY not in vault:
        vault[TAGS_KEY] = {}
    vault[TAGS_KEY][entry] = sorted(set(tags))
    return vault


def add_tag(vault: dict, entry: str, tag: str) -> dict:
    """Add a single tag to a vault entry."""
    existing = get_tags(vault, entry)
    if tag not in existing:
        existing.append(tag)
    return set_tags(vault, entry, existing)


def remove_tag(vault: dict, entry: str, tag: str) -> dict:
    """Remove a single tag from a vault entry (no-op if missing)."""
    existing = get_tags(vault, entry)
    existing = [t for t in existing if t != tag]
    return set_tags(vault, entry, existing)


def filter_by_tag(vault: dict, tag: str) -> List[str]:
    """Return entry names that have the given tag."""
    meta = vault.get(TAGS_KEY, {})
    return [entry for entry, tags in meta.items() if tag in tags]


def all_tags(vault: dict) -> Dict[str, List[str]]:
    """Return a mapping of entry -> tags for all tagged entries."""
    return {k: list(v) for k, v in vault.get(TAGS_KEY, {}).items()}


def format_tags_report(vault: dict) -> str:
    """Format a human-readable report of all tags in the vault."""
    mapping = all_tags(vault)
    if not mapping:
        return "No tags defined."
    lines = []
    for entry, tags in sorted(mapping.items()):
        tag_str = ", ".join(tags) if tags else "(none)"
        lines.append(f"  {entry}: {tag_str}")
    return "Tags:\n" + "\n".join(lines)
