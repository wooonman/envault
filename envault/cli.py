"""CLI entry point for envault using argparse."""

import argparse
import getpass
import sys

from envault.vault import lock, unlock


def get_password(prompt: str = "Vault password: ") -> str:
    """Read password from env var ENVAULT_PASSWORD or prompt the user."""
    import os
    pw = os.environ.get("ENVAULT_PASSWORD")
    if pw:
        return pw
    return getpass.getpass(prompt)


def cmd_lock(args: argparse.Namespace) -> None:
    password = get_password("Password to encrypt: ")
    try:
        lock(args.env_file, password, args.vault)
        print(f"Locked {args.env_file} → {args.vault}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_unlock(args: argparse.Namespace) -> None:
    password = get_password("Password to decrypt: ")
    try:
        unlock(args.env_file, password, args.vault)
        print(f"Unlocked {args.env_file} from {args.vault}")
    except (KeyError, Exception) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Encrypt and version-control .env files safely.",
    )
    parser.add_argument("--vault", default=".env.vault", help="Path to vault file")
    sub = parser.add_subparsers(dest="command", required=True)

    lock_p = sub.add_parser("lock", help="Encrypt a .env file into the vault")
    lock_p.add_argument("env_file", nargs="?", default=".env")
    lock_p.set_defaults(func=cmd_lock)

    unlock_p = sub.add_parser("unlock", help="Decrypt a .env file from the vault")
    unlock_p.add_argument("env_file", nargs="?", default=".env")
    unlock_p.set_defaults(func=cmd_unlock)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
