"""Watch a .env file for changes and auto-lock into the vault."""

import os
import time
import hashlib
from pathlib import Path
from typing import Callable, Optional


def _file_hash(path: Path) -> Optional[str]:
    """Return MD5 hex digest of file contents, or None if file missing."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except FileNotFoundError:
        return None


def watch_env(
    env_path: Path,
    on_change: Callable[[Path], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Poll *env_path* every *interval* seconds.
    Call *on_change(env_path)* whenever the file content changes.

    Parameters
    ----------
    env_path:       Path to the .env file to watch.
    on_change:      Callback invoked with the changed path.
    interval:       Polling interval in seconds.
    max_iterations: Stop after this many iterations (useful for tests).
    """
    env_path = Path(env_path)
    last_hash = _file_hash(env_path)
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
        current_hash = _file_hash(env_path)
        if current_hash is not None and current_hash != last_hash:
            last_hash = current_hash
            on_change(env_path)
        iterations += 1


def format_watch_event(env_path: Path, vault_path: Path) -> str:
    """Return a human-readable message for a watch-triggered lock event."""
    return (
        f"[watch] detected change in {env_path} "
        f"→ locked into {vault_path}"
    )
