"""Detect and report keys whose values look like unfilled placeholders."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from envault.vault import load_vault
from envault.crypto import decrypt_from_b64

# Patterns that suggest a value is a placeholder / not yet filled in
_PLACEHOLDER_PATTERNS = [
    re.compile(r"^CHANGE[_-]?ME$", re.IGNORECASE),
    re.compile(r"^TODO$", re.IGNORECASE),
    re.compile(r"^FIXME$", re.IGNORECASE),
    re.compile(r"^YOUR[_-]", re.IGNORECASE),
    re.compile(r"^<.+>$"),          # <MY_VALUE>
    re.compile(r"^\[.+\]$"),        # [MY_VALUE]
    re.compile(r"^\$\{.+\}$"),      # ${MY_VALUE}
    re.compile(r"^\*+$"),           # *** or similar
    re.compile(r"^PLACEHOLDER$", re.IGNORECASE),
    re.compile(r"^REPLACE[_-]?ME$", re.IGNORECASE),
    re.compile(r"^N/?A$", re.IGNORECASE),
    re.compile(r"^EXAMPLE[_-]", re.IGNORECASE),
    re.compile(r"^DUMMY", re.IGNORECASE),
]


@dataclass
class PlaceholderEntry:
    key: str
    value: str
    pattern: str

    def __str__(self) -> str:
        return f"{self.key!r} = {self.value!r}  (matches: {self.pattern})"


@dataclass
class PlaceholderResult:
    entries: List[PlaceholderEntry] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return bool(self.entries)

    def __str__(self) -> str:
        if not self.entries:
            return "No placeholder values detected."
        lines = [f"{len(self.entries)} placeholder(s) detected:"]
        for e in self.entries:
            lines.append(f"  {e}")
        return "\n".join(lines)


def _is_placeholder(value: str) -> str | None:
    """Return the pattern description if value looks like a placeholder, else None."""
    for pat in _PLACEHOLDER_PATTERNS:
        if pat.search(value.strip()):
            return pat.pattern
    return None


def check_placeholders(vault_path: str, password: str) -> PlaceholderResult:
    """Decrypt vault entries and flag any that look like unfilled placeholders."""
    vault = load_vault(vault_path)
    result = PlaceholderResult()
    for key, meta in vault.items():
        if key.startswith("_"):
            continue
        try:
            value = decrypt_from_b64(meta["value"], password)
        except Exception:
            continue
        matched = _is_placeholder(value)
        if matched:
            result.entries.append(PlaceholderEntry(key=key, value=value, pattern=matched))
    result.entries.sort(key=lambda e: e.key)
    return result
