"""Utilities for comparing vault entries and showing diffs."""

from typing import Dict, List, Tuple


def parse_env_lines(text: str) -> Dict[str, str]:
    """Parse .env file content into a key-value dict, ignoring comments/blanks."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def diff_envs(
    old: Dict[str, str], new: Dict[str, str]
) -> Tuple[List[str], List[str], List[str]]:
    """Return (added, removed, changed) key lists between two env dicts."""
    old_keys = set(old)
    new_keys = set(new)

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = sorted(
        k for k in old_keys & new_keys if old[k] != new[k]
    )
    return added, removed, changed


def format_diff(
    old: Dict[str, str],
    new: Dict[str, str],
    mask_values: bool = True,
) -> str:
    """Return a human-readable diff string between two env dicts."""
    added, removed, changed = diff_envs(old, new)
    lines = []

    def _val(v: str) -> str:
        return "***" if mask_values else v

    for k in added:
        lines.append(f"  + {k}={_val(new[k])}")
    for k in removed:
        lines.append(f"  - {k}={_val(old[k])}")
    for k in changed:
        lines.append(f"  ~ {k}: {_val(old[k])} -> {_val(new[k])}")

    if not lines:
        return "  (no changes)"
    return "\n".join(lines)
