"""CLI subcommand: envault validate — check vault entries against a schema."""

import json
import sys

from envault.env_validate import validate_vault, format_validation_report
from envault.cli import get_password


def cmd_validate(args) -> None:
    try:
        with open(args.schema, "r") as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"Error: schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in schema: {e}", file=sys.stderr)
        sys.exit(1)

    password = get_password(confirm=False)

    try:
        result = validate_vault(args.vault, password, schema)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(format_validation_report(result))

    if not result.ok:
        sys.exit(2)


def add_validate_subcommand(subparsers) -> None:
    p = subparsers.add_parser(
        "validate",
        help="Validate vault entries against a JSON schema of rules",
    )
    p.add_argument("vault", help="Path to the .vault file")
    p.add_argument(
        "schema",
        help=(
            "Path to a JSON schema file mapping key names to rule objects. "
            "Example: {\"API_KEY\": {\"required\": true, \"min_length\": 16}}"
        ),
    )
    p.set_defaults(func=cmd_validate)
