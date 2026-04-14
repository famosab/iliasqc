"""Command-line interface for iliasqc."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from iliasqc.combine import (
    export_combinations_csv,
    format_combinations_table,
    generate_quiz_combinations,
)
from iliasqc.convert import txt_to_qti, txt_to_zip
from iliasqc.template import generate_template


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``iliasqc`` command."""
    parser = argparse.ArgumentParser(
        prog="iliasqc",
        description="Convert txt question files into ILIAS-compatible zip archives.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    convert_parser = subparsers.add_parser(
        "convert", help="Convert a question file to ILIAS zip archive"
    )
    convert_parser.add_argument("input", help="Path to the input .txt file.")
    convert_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Path for the output .zip file (default: same directory as input).",
    )
    convert_parser.add_argument(
        "-t", "--title", dest="title", default=None, help="Override the pool title."
    )
    convert_parser.add_argument(
        "-d", "--description", default=None, help="Override the pool description."
    )
    convert_parser.add_argument(
        "-p",
        "--points",
        type=float,
        default=None,
        help="Only include questions with this point value.",
    )

    combine_parser = subparsers.add_parser(
        "combine", help="Generate pools and find quiz combinations"
    )
    combine_parser.add_argument("input", help="Path to the input .txt file.")
    combine_parser.add_argument(
        "-t",
        "--target",
        dest="target_points",
        type=float,
        help="Target total points for quiz combinations.",
    )
    combine_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Directory for output files (default: same directory as input).",
    )
    combine_parser.add_argument(
        "-c",
        "--combinations",
        type=int,
        default=10,
        help="Maximum number of combinations to show (default: 10).",
    )
    combine_parser.add_argument(
        "--csv-only", action="store_true", help="Only output CSV, skip the table display."
    )

    qti_parser = subparsers.add_parser("qti", help="Convert a question file to QTI XML format")
    qti_parser.add_argument("input", help="Path to the input .txt file.")
    qti_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Path for the output .xml file (default: same directory as input).",
    )
    qti_parser.add_argument(
        "-p",
        "--points",
        type=float,
        default=None,
        help="Only include questions with this point value.",
    )

    template_parser = subparsers.add_parser("template", help="Generate a question file template")
    template_parser.add_argument(
        "-o",
        "--output",
        default="questions_template.txt",
        help="Path for the template file (default: questions_template.txt).",
    )
    template_parser.add_argument(
        "--no-examples", action="store_true", help="Generate a template without example questions."
    )

    args = parser.parse_args(argv)

    if args.command is None:
        args.command = "convert"
        if argv and len(argv) > 0 and not argv[0].startswith("-"):
            args.input = argv[0]
            if "-o" in argv:
                idx = argv.index("-o") + 1
                if idx < len(argv):
                    args.output = argv[idx]
            else:
                args.output = None
        elif "-o" in argv or "--output" in argv:
            parser.print_help()
            return 0
        else:
            parser.print_help()
            return 0

    if args.command == "convert":
        try:
            output = txt_to_zip(
                args.input,
                args.output,
                title=args.title,
                description=args.description,
                filter_points=args.points,
            )
            print(f"Created: {output}")
            return 0
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.command == "combine":
        if args.target_points is None:
            print("Error: --target/-t is required for combine command", file=sys.stderr)
            return 1
        try:
            pools, combinations = generate_quiz_combinations(
                args.input,
                args.target_points,
                output_dir=args.output,
            )

            output_dir = Path(args.output) if args.output else Path(args.input).parent

            csv_path = export_combinations_csv(
                output_dir,
                combinations[: args.combinations],
                args.target_points,
            )
            print(f"Created CSV: {csv_path}")

            if not args.csv_only:
                table = format_combinations_table(
                    combinations[: args.combinations],
                    pools,
                    args.target_points,
                )
                print()
                print(table)

            print(f"\nGenerated {len(pools)} pools:")
            for pool in pools:
                print(f"  - {pool.zip_filename}: {pool.question_count} questions")

            return 0
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.command == "qti":
        try:
            output = txt_to_qti(args.input, args.output, filter_points=args.points)
            print(f"Created: {output}")
            return 0
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.command == "template":
        try:
            output = generate_template(
                args.output,
                include_examples=not args.no_examples,
            )
            print(f"Created template: {output}")
            return 0
        except FileExistsError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
