"""Merge two vault files, with conflict detection and resolution strategies."""

from typing import Dict, List, Tuple

Conflict = Tuple[str, str, str]  # (key, value_a, value_b)


def merge_envs(
    base: Dict[str, str],
    incoming: Dict[str, str],
    strategy: str = "ours",
) -> Tuple[Dict[str, str], List[Conflict]]:
    """
    Merge two env dicts.

    strategy:
        'ours'     - keep base value on conflict
        'theirs'   - keep incoming value on conflict
        'error'    - raise ValueError on first conflict

    Returns (merged_dict, list_of_conflicts).
    """
    if strategy not in ("ours", "theirs", "error"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    merged: Dict[str, str] = dict(base)
    conflicts: List[Conflict] = []

    for key, val_b in incoming.items():
        if key not in merged:
            # New key — just add it
            merged[key] = val_b
        elif merged[key] != val_b:
            conflicts.append((key, merged[key], val_b))
            if strategy == "error":
                raise ValueError(
                    f"Merge conflict on key {key!r}: "
                    f"{merged[key]!r} vs {val_b!r}"
                )
            elif strategy == "theirs":
                merged[key] = val_b
            # 'ours' keeps merged[key] as-is

    return merged, conflicts


def format_conflicts(conflicts: List[Conflict]) -> str:
    """Return a human-readable summary of merge conflicts."""
    if not conflicts:
        return "No conflicts."
    lines = [f"Conflicts ({len(conflicts)}):"]
    for key, val_a, val_b in conflicts:
        lines.append(f"  {key}")
        lines.append(f"    ours:    {val_a}")
        lines.append(f"    theirs:  {val_b}")
    return "\n".join(lines)
