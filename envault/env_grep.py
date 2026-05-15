"""Search vault entries by value pattern (grep-style)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault
from envault.crypto import decrypt_from_b64


@dataclass
class GrepMatch:
    key: str
    value: str
    line_number: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.key}={self.value}"


@dataclass
class GrepResult:
    pattern: str
    matches: List[GrepMatch] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.matches)

    def __str__(self) -> str:
        if not self.matches:
            return f"No matches for pattern: {self.pattern}"
        lines = [f"Matches for '{self.pattern}':"] + [
            f"  {m}" for m in self.matches
        ]
        return "\n".join(lines)


class GrepError(Exception):
    pass


def grep_vault(
    vault_path: str,
    password: str,
    pattern: str,
    *,
    keys_only: bool = False,
    ignore_case: bool = False,
    invert: bool = False,
    use_regex: bool = False,
) -> GrepResult:
    """Search decrypted vault values (or keys) for a pattern."""
    vault = load_vault(vault_path)
    entries = {k: v for k, v in vault.items() if not k.startswith("__")}

    flags = re.IGNORECASE if ignore_case else 0

    if use_regex:
        try:
            compiled = re.compile(pattern, flags)
        except re.error as exc:
            raise GrepError(f"Invalid regex pattern: {exc}") from exc
        match_fn = lambda text: bool(compiled.search(text))
    else:
        needle = pattern.lower() if ignore_case else pattern
        match_fn = lambda text: needle in (text.lower() if ignore_case else text)

    result = GrepResult(pattern=pattern)
    for idx, (key, enc_value) in enumerate(sorted(entries.items()), start=1):
        try:
            value = decrypt_from_b64(enc_value, password)
        except Exception:
            continue

        target = key if keys_only else value
        hit = match_fn(target)
        if invert:
            hit = not hit
        if hit:
            result.matches.append(GrepMatch(key=key, value=value, line_number=idx))

    return result


def format_grep_report(result: GrepResult, *, show_line_numbers: bool = False) -> str:
    if not result.matches:
        return f"No matches for '{result.pattern}'."
    lines = []
    for m in result.matches:
        prefix = f"{m.line_number}:" if show_line_numbers and m.line_number else ""
        lines.append(f"{prefix}{m.key}={m.value}")
    return "\n".join(lines)
