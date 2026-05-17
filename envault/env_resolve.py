"""Resolve variable references within a vault (e.g. VALUE=${OTHER_KEY})."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault
from envault.crypto import decrypt_from_b64

REF_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


class ResolveError(Exception):
    pass


@dataclass
class ResolveResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved: List[str] = field(default_factory=list)
    cycles: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.resolved:
            lines.append(f"Resolved {len(self.resolved)} reference(s):")
            for k, v in sorted(self.resolved.items()):
                lines.append(f"  {k} = {v}")
        if self.unresolved:
            lines.append(f"Unresolved reference(s): {', '.join(sorted(self.unresolved))}")
        if self.cycles:
            lines.append(f"Cycle(s) detected: {', '.join(sorted(self.cycles))}")
        return "\n".join(lines) if lines else "No variable references found."


def _decrypt_all(vault_path: str, password: str) -> Dict[str, str]:
    vault = load_vault(vault_path)
    entries = {k: v for k, v in vault.items() if not k.startswith("__")}
    plain: Dict[str, str] = {}
    for key, ciphertext in entries.items():
        try:
            plain[key] = decrypt_from_b64(ciphertext, password)
        except Exception:
            pass
    return plain


def resolve_references(
    vault_path: str,
    password: str,
    max_depth: int = 10,
) -> ResolveResult:
    """Decrypt all entries and resolve ${VAR} references transitively."""
    plain = _decrypt_all(vault_path, password)
    result = ResolveResult()

    def _resolve(key: str, seen: Optional[List[str]] = None) -> Optional[str]:
        if seen is None:
            seen = []
        if key in seen:
            result.cycles.append(key)
            return None
        if len(seen) > max_depth:
            result.unresolved.append(key)
            return None
        value = plain.get(key)
        if value is None:
            return None
        refs = REF_PATTERN.findall(value)
        if not refs:
            return value
        new_seen = seen + [key]
        for ref in refs:
            resolved_ref = _resolve(ref, new_seen)
            if resolved_ref is None:
                if ref not in result.cycles:
                    result.unresolved.append(key)
                return None
            value = value.replace(f"${{{ref}}}", resolved_ref)
        return value

    for key in plain:
        if REF_PATTERN.search(plain[key]):
            resolved = _resolve(key)
            if resolved is not None:
                result.resolved[key] = resolved

    return result
