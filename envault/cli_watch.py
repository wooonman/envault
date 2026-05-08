"""CLI subcommand: envault watch — auto-lock .env on file changes."""

import sys
from pathlib import Path

from envault.watch import watch_env, format_watch_event
from envault.vault import lock
from envault.cli import get_password


def cmd_watch(args) -> None:
    env_path = Path(args.env_file)
    vault_path = Path(args.vault_file)

    if not env_path.exists():
        print(f"error: {env_path} does not exist", file=sys.stderr)
        sys.exit(1)

    password = get_password(confirm=False)

    print(f"Watching {env_path} for changes (Ctrl+C to stop) …")

    def on_change(path: Path) -> None:
        try:
            lock(env_path=path, vault_path=vault_path, password=password)
            print(format_watch_event(path, vault_path))
        except Exception as exc:  # noqa: BLE001
            print(f"[watch] error locking: {exc}", file=sys.stderr)

    try:
        watch_env(
            env_path=env_path,
            on_change=on_change,
            interval=args.interval,
        )
    except KeyboardInterrupt:
        print("\nWatch stopped.")


def add_watch_subcommand(subparsers) -> None:
    p = subparsers.add_parser(
        "watch",
        help="Watch a .env file and auto-lock it into the vault on every change.",
    )
    p.add_argument(
        "env_file",
        help="Path to the .env file to watch (e.g. .env)",
    )
    p.add_argument(
        "vault_file",
        help="Path to the vault file to write (e.g. .env.vault)",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 1.0)",
    )
    p.set_defaults(func=cmd_watch)
