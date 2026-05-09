"""Per-key notes/comments stored in the vault metadata."""

from __future__ import annotations

from typing import Optional

from envault.vault import load_vault, save_vault

_META_KEY = "__notes__"


class NoteError(Exception):
    pass


def _get_notes_map(vault: dict) -> dict:
    return vault.get(_META_KEY, {})


def get_note(vault_path: str, key: str) -> Optional[str]:
    """Return the note for *key*, or None if no note exists."""
    vault = load_vault(vault_path)
    return _get_notes_map(vault).get(key)


def set_note(vault_path: str, key: str, text: str, password: str) -> None:
    """Attach *text* as a note for *key*. Key must exist in the vault."""
    vault = load_vault(vault_path)
    if key not in vault:
        raise NoteError(f"Key '{key}' not found in vault")
    notes = _get_notes_map(vault)
    notes[key] = text
    vault[_META_KEY] = notes
    save_vault(vault_path, vault)


def clear_note(vault_path: str, key: str) -> bool:
    """Remove the note for *key*. Returns True if a note existed."""
    vault = load_vault(vault_path)
    notes = _get_notes_map(vault)
    if key not in notes:
        return False
    del notes[key]
    vault[_META_KEY] = notes
    save_vault(vault_path, vault)
    return True


def list_notes(vault_path: str) -> dict[str, str]:
    """Return all key -> note mappings."""
    vault = load_vault(vault_path)
    return dict(_get_notes_map(vault))


def format_notes_report(notes: dict[str, str]) -> str:
    if not notes:
        return "No notes found."
    lines = []
    for key, text in sorted(notes.items()):
        lines.append(f"  {key}: {text}")
    return "Notes:\n" + "\n".join(lines)
