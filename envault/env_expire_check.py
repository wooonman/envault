"""Check which vault entries are expired or expiring soon."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from envault.vault import load_vault
from envault.ttl import get_ttl_data


@dataclass
class ExpiryEntry:
    key: str
    expires_at: Optional[str]
    expired: bool
    days_remaining: Optional[float]

    def __str__(self) -> str:
        if self.expired:
            return f"[EXPIRED]  {self.key}  (expired {self.expires_at})"
        if self.days_remaining is not None:
            return f"[WARNING]  {self.key}  ({self.days_remaining:.1f} days remaining, expires {self.expires_at})"
        return f"[OK]       {self.key}  (no expiry set)"


@dataclass
class ExpiryCheckResult:
    entries: List[ExpiryEntry] = field(default_factory=list)

    @property
    def expired(self) -> List[ExpiryEntry]:
        return [e for e in self.entries if e.expired]

    @property
    def expiring_soon(self) -> List[ExpiryEntry]:
        return [
            e for e in self.entries
            if not e.expired and e.days_remaining is not None
        ]

    def __str__(self) -> str:
        lines = [str(e) for e in self.entries]
        lines.append(f"\nTotal: {len(self.entries)}  Expired: {len(self.expired)}  Expiring soon: {len(self.expiring_soon)}")
        return "\n".join(lines)


def check_expiry(vault_path: str, warn_days: int = 7) -> ExpiryCheckResult:
    """Return expiry status for all vault entries."""
    vault = load_vault(vault_path)
    ttl_data = get_ttl_data(vault_path)
    now = datetime.now(timezone.utc)
    result = ExpiryCheckResult()

    for key in sorted(vault.get("entries", {})):
        expires_at = ttl_data.get(key)
        if expires_at is None:
            result.entries.append(ExpiryEntry(key=key, expires_at=None, expired=False, days_remaining=None))
            continue

        expiry_dt = datetime.fromisoformat(expires_at)
        delta = expiry_dt - now
        days = delta.total_seconds() / 86400
        expired = days <= 0
        days_remaining = None if expired else days
        if days_remaining is not None and days_remaining > warn_days:
            days_remaining = None  # only flag if within warn window
            result.entries.append(ExpiryEntry(key=key, expires_at=expires_at, expired=False, days_remaining=None))
        else:
            result.entries.append(ExpiryEntry(key=key, expires_at=expires_at, expired=expired, days_remaining=days_remaining if not expired else None))

    return result
