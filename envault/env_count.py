"""Count and summarize vault entries with optional filtering."""

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault
from envault.tags import get_tags
from envault.pin import get_pins


@dataclass
class CountResult:
    total: int
    pinned: int
    tagged: int
    by_tag: dict
    by_prefix: dict

    def __str__(self) -> str:
        lines = [f"Total entries : {self.total}"]
        lines.append(f"Pinned        : {self.pinned}")
        lines.append(f"Tagged        : {self.tagged}")
        if self.by_tag:
            lines.append("By tag:")
            for tag, count in sorted(self.by_tag.items()):
                lines.append(f"  {tag:<20} {count}")
        if self.by_prefix:
            lines.append("By prefix:")
            for prefix, count in sorted(self.by_prefix.items()):
                lines.append(f"  {prefix:<20} {count}")
        return "\n".join(lines)


def count_entries(
    vault_path: str,
    prefix: Optional[str] = None,
    group_by_prefix: bool = False,
    prefix_sep: str = "_",
) -> CountResult:
    """Count vault entries, optionally grouped by tag or key prefix."""
    vault = load_vault(vault_path)
    entries = {
        k: v
        for k, v in vault.items()
        if not k.startswith("__")
    }

    if prefix:
        entries = {k: v for k, v in entries.items() if k.startswith(prefix)}

    keys = list(entries.keys())
    total = len(keys)

    pins = set(get_pins(vault_path))
    pinned = sum(1 for k in keys if k in pins)

    tag_data = get_tags(vault_path)
    by_tag: dict = {}
    tagged_keys: set = set()
    for key in keys:
        key_tags = tag_data.get(key, [])
        for t in key_tags:
            by_tag[t] = by_tag.get(t, 0) + 1
            tagged_keys.add(key)
    tagged = len(tagged_keys)

    by_prefix: dict = {}
    if group_by_prefix:
        for key in keys:
            parts = key.split(prefix_sep, 1)
            pfx = parts[0] if len(parts) > 1 else "(none)"
            by_prefix[pfx] = by_prefix.get(pfx, 0) + 1

    return CountResult(
        total=total,
        pinned=pinned,
        tagged=tagged,
        by_tag=by_tag,
        by_prefix=by_prefix,
    )
