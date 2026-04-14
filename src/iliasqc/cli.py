"""Command-line interface for iliasqc."""

from __future__ import annotations

import argparse
import sys

from iliasqc.convert import txt_to_zip


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``iliasqc`` command."""
    parser = argparse.ArgumentParser(
        prog="iliasqc",
        description="Convert txt question files into Ilias-compatible zip archives.",
    )
    parser.add_argument("input", help="Path to the input .txt file.")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Path for the output .zip file (default: same directory as input).",
    )
    args = parser.parse_args(argv)

    output = txt_to_zip(args.input, args.output)
    print(f"Created: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
