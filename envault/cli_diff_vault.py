"""CLI subcommand: envault diff-vaults — compare two vault files."""

import argparse
import sys

from envault.env_diff_vault import diff_vaults, VaultDiffError, format_vault_diff
from envault.cli import get_password


def cmd_diff_vaults(args: argparse.Namespace) -> None:
    password_a = get_password(prompt=f"Password for {args.vault_a}: ")

    if args.same_password:
        password_b = password_a
    else:
        password_b = get_password(prompt=f"Password for {args.vault_b}: ")

    try:
        result = diff_vaults(
            args.vault_a,
            args.vault_b,
            password_a=password_a,
            password_b=password_b,
        )
    except VaultDiffError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not result.has_differences():
        print("Vaults are identical.")
        return

    summary_parts = []
    if result.added:
        summary_parts.append(f"{len(result.added)} added")
    if result.removed:
        summary_parts.append(f"{len(result.removed)} removed")
    if result.changed:
        summary_parts.append(f"{len(result.changed)} changed")
    if result.unchanged:
        summary_parts.append(f"{len(result.unchanged)} unchanged")

    print("Vault diff summary:", ", ".join(summary_parts))
    print()
    print(format_vault_diff(result))


def add_diff_vaults_subcommand(subparsers) -> None:
    parser = subparsers.add_parser(
        "diff-vaults",
        help="Compare two vault files and show key-level differences",
    )
    parser.add_argument("vault_a", help="Path to the first vault file")
    parser.add_argument("vault_b", help="Path to the second vault file")
    parser.add_argument(
        "--same-password",
        action="store_true",
        default=False,
        help="Use the same password for both vaults (avoids second prompt)",
    )
    parser.set_defaults(func=cmd_diff_vaults)
