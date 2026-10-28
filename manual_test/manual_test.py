#!/usr/bin/env python3
"""Generate ILIAS-uploadable quiz pools for manual testing.

Run this after activating your Python 3.12+ env and installing the package.

Usage:
    conda activate iliasqc
    python manual_test.py

All outputs land in ``manual_test_output/`` in the project root.
Each ZIP is placed inside a subfolder named after the pool's descriptive title.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

# Use the iliasqc conda environment's Python (requires Python >= 3.12)
PYTHON = "/Users/famke/miniconda3/envs/iliasqc/bin/python"


# ── Sample files ──────────────────────────────────────────────────────────

SAMPLE_FILES = {
    "single_choice.txt": """# TITLE: Single Choice Questions
# DESCRIPTION: Basic single-choice questions [s] type

[t][s] What is the capital of France? @1
_ Paris
- London
- Berlin
- Madrid

[t][s] Which planet is known as the Red Planet? @2
_ Mars
- Venus
- Jupiter
- Saturn

[t][s] What is 2 + 2? @1
_ 4
- 5
- 3
- 6
""",
    "multiple_choice.txt": """# TITLE: Multiple Choice Questions
# DESCRIPTION: Questions with multiple correct answers [m] type

[t][m] Which of these are fruits? @2
_ Apple
_ Banana
- Carrot
- Broccoli
_ Cherry

[t][m] Select all prime numbers: @1
_ 2
_ 7
- 4
- 9
_ 13

[t][m] Which languages are statically typed? @2
_ Java
- Python
_ TypeScript
- JavaScript
_ Go
""",
    "gap_fill.txt": """# TITLE: Gap Fill Questions
# DESCRIPTION: Cloze / gap-fill questions [g] type

[t][g] Germany's Capital @1
The capital is [gap]Berlin[/gap].
Correct: Berlin
- Paris
- London

[t][g] Water Formula @2
H[gap]2[/gap]O.
Correct: 2
- O
- 3
- H
""",
    "mixed_pool.txt": """# TITLE: Mixed Question Pool
# DESCRIPTION: All types, mixed points — for combination testing

[t][s] What does HTML stand for? @1
_ HyperText Markup Language
- High Tech Modern Language
- Hyper Transfer Markup Language
- Home Tool Markup Language

[t][m] Which are programming languages? @2
_ Python
_ Rust
- Markdown
- Excel
_ Kotlin

[t][g] HTTP Status Code @1
The status code for "Not Found" is [gap]404[/gap].
Correct: 404
- 500
- 200
- 301

[t][s] First iPhone release year? @2
_ 2007
- 2005
- 2009
- 2010

[t][m] Select all web browsers: @1
_ Firefox
_ Chrome
- Windows
_ Safari
- macOS
""",
}


def safe_dir(output_dir: Path, name: str) -> Path:
    """Create (or reuse) a subfolder, sanitising the name."""
    # ILIAS folder names can't contain /, replace with _
    sanitised = name.replace("/", "_")
    # Truncate to avoid overly long paths
    if len(sanitised) > 60:
        sanitised = sanitised[:57] + "..."
    target = output_dir / sanitised
    target.mkdir(parents=True, exist_ok=True)
    return target


# ── Helpers ───────────────────────────────────────────────────────────────

def run(cmd: list[str], description: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {description}")
    print(f"  Command: python -m iliasqc.cli {' '.join(cmd)}")
    print(f"{'=' * 60}")
    result = subprocess.run(
        [PYTHON, "-m", "iliasqc.cli"] + cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    if result.returncode != 0:
        print(f"WARNING: exit code {result.returncode}", file=sys.stderr)


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n{'#' * 60}")
    print(f"  ILIAS QC Manual Test → {OUTPUT_DIR}")
    print(f"{'#' * 60}")

    # Clean old output
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.rglob("*"):
            if f.is_file():
                f.unlink()
        (OUTPUT_DIR / "combine_results").mkdir(exist_ok=True)
    else:
        OUTPUT_DIR.mkdir()
        (OUTPUT_DIR / "combine_results").mkdir()

    # Track generated zips: (folder_path, zip_path)
    all_zips: list[tuple[Path, Path]] = []

    # 1. Convert each sample file — place each ZIP in a titled folder
    for name, content in SAMPLE_FILES.items():
        input_path = OUTPUT_DIR / name
        input_path.write_text(content)

        # Extract the # TITLE: line to get the folder name
        title_line = [l for l in content.splitlines() if l.startswith("# TITLE:")]
        folder_name = title_line[0].replace("# TITLE:", "").strip() if title_line else name.replace(".txt", "")

        folder = safe_dir(OUTPUT_DIR, folder_name)

        # We'll put the ILIAS-named ZIP into the folder
        zip_path = folder / "pool.zip"  # generic name — real name comes from CLI output

        run(
            ["convert", str(input_path), "-o", str(zip_path)],
            f"Convert {name} → {folder_name}",
        )

    # 2. --title / --description overrides — separate folder
    override_folder = safe_dir(OUTPUT_DIR, "Override Test")
    run(
        ["convert", str(OUTPUT_DIR / "single_choice.txt"), "-o", str(override_folder / "pool.zip"),
         "-t", "Override Title", "-d", "Custom description for testing overrides"],
        "Convert with --title / --description overrides",
    )

    # 3. --points filter — separate folder
    filter_folder = safe_dir(OUTPUT_DIR, "Points Filter (1 pt)")
    run(
        ["convert", str(OUTPUT_DIR / "mixed_pool.txt"), "-o", str(filter_folder / "pool.zip"), "-p", "1"],
        "Convert with --points 1 filter",
    )

    # 4. combine: target 3 pts
    combine_dir = OUTPUT_DIR / "combine_results"
    run(
        ["combine", str(OUTPUT_DIR / "mixed_pool.txt"), "-t", "3", "-o", str(combine_dir), "-c", "5"],
        "Combine: target=3 pts",
    )

    # 5. combine: target 5 pts
    run(
        ["combine", str(OUTPUT_DIR / "mixed_pool.txt"), "-t", "5", "-o", str(combine_dir), "-c", "5"],
        "Combine: target=5 pts",
    )

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'#' * 60}")
    print(f"  DONE — generated:")
    print(f"{'#' * 60}")

    # Walk all zips and print with folder context
    for folder in sorted(OUTPUT_DIR.iterdir()):
        if not folder.is_dir():
            continue
        zips = list(folder.glob("*.zip"))
        if not zips:
            continue
        print(f"\n  📂 {folder.name}/")
        for z in sorted(zips):
            print(f"      📦 {z.name}  ({z.stat().st_size:>8,} bytes)")

    # Combine results
    combine_dir = OUTPUT_DIR / "combine_results"
    if combine_dir.exists():
        csvs = list(combine_dir.glob("*.csv"))
        if csvs:
            print(f"\n  📊 CSV:  {csvs[0].name}  ({csvs[0].stat().st_size:>8,} bytes)")
        zips = list(combine_dir.glob("*.zip"))
        for z in sorted(zips):
            print(f"      📦 {z.name}  ({z.stat().st_size:>8,} bytes)")

    print(f"\nUpload the .zip files to ILIAS to test import.")
    print(f"Each .zip lives inside a titled folder for easy identification.")


if __name__ == "__main__":
    main()