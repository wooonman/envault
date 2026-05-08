"""CLI subcommand: render a template file using vault entries."""

import argparse
import sys

from envault.cli import get_password
from envault.template import (
    render_template_file,
    list_placeholders,
    format_render_report,
    TemplateError,
)


def cmd_template(args: argparse.Namespace) -> None:
    password = get_password(confirm=False)
    try:
        template_src = open(args.template).read()
        placeholders = list_placeholders(template_src)

        rendered = render_template_file(
            template_path=args.template,
            vault_path=args.vault,
            password=password,
            output_path=args.output if args.output else None,
        )
    except TemplateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as exc:
        print(f"File not found: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        print(format_render_report(rendered, placeholders))
        print(f"Written to: {args.output}")
    else:
        print(rendered, end="")


def add_template_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "template",
        help="render a template file substituting vault values",
    )
    p.add_argument("template", help="path to template file with {{KEY}} placeholders")
    p.add_argument(
        "--vault",
        default=".envault",
        help="vault file to read (default: .envault)",
    )
    p.add_argument(
        "--output",
        default=None,
        help="write rendered output to this file (default: stdout)",
    )
    p.set_defaults(func=cmd_template)
