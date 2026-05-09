"""Snapshot: capture and restore full vault state by name."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SNAPSHOT_KEY = "__snapshots__"


class SnapshotError(Exception):
    pass


def _get_snapshot_map(vault: dict) -> dict[str, Any]:
    return vault.get(SNAPSHOT_KEY, {})


def list_snapshots(vault: dict) -> list[str]:
    """Return sorted list of snapshot names."""
    return sorted(_get_snapshot_map(vault).keys())


def save_snapshot(vault: dict, name: str) -> dict:
    """Capture current vault entries under *name*. Returns updated vault."""
    if not name or not name.strip():
        raise SnapshotError("Snapshot name must not be empty.")
    entries = {k: v for k, v in vault.items() if not k.startswith("__")}
    snapshots = _get_snapshot_map(vault).copy()
    snapshots[name] = entries
    vault = dict(vault)
    vault[SNAPSHOT_KEY] = snapshots
    return vault


def restore_snapshot(vault: dict, name: str) -> dict:
    """Restore vault entries from snapshot *name*. Returns updated vault."""
    snapshots = _get_snapshot_map(vault)
    if name not in snapshots:
        raise SnapshotError(f"Snapshot '{name}' not found.")
    restored = snapshots[name]
    # Keep all __ metadata keys, replace plain entries
    new_vault = {k: v for k, v in vault.items() if k.startswith("__")}
    new_vault.update(restored)
    return new_vault


def delete_snapshot(vault: dict, name: str) -> dict:
    """Delete snapshot *name*. Returns updated vault."""
    snapshots = _get_snapshot_map(vault).copy()
    if name not in snapshots:
        raise SnapshotError(f"Snapshot '{name}' not found.")
    del snapshots[name]
    vault = dict(vault)
    vault[SNAPSHOT_KEY] = snapshots
    return vault


def format_snapshot_list(names: list[str]) -> str:
    if not names:
        return "No snapshots saved."
    lines = ["Snapshots:"]
    for n in names:
        lines.append(f"  - {n}")
    return "\n".join(lines)
