"""Template file generator for iliasqc."""

from __future__ import annotations

from pathlib import Path

TEMPLATE_CONTENT_BASIC = """# TITLE: My Question Pool
# DESCRIPTION: A collection of questions for my ILIAS course

# ============================================================
# Question Syntax:
#   [t] - Question start marker (required)
#   [s] - Single choice question
#   [m] - Multiple choice question
#   [g] - Gap-fill question
#   _  - Correct answer (for MC questions)
#   -  - Incorrect answer (for MC questions)
#   [gap]content[/gap] - Gap to fill
#   @N - Points for the question (e.g., @2)
# ============================================================

[t][s] Single Choice Question Title @1
Question text goes here.
_ Correct answer
- Incorrect answer
- Another wrong answer

[t][m] Multiple Choice Question Title @2
Which options are correct?
- Wrong answer
_ Correct answer
- Another wrong answer
_ Another correct answer

[t][g] Gap-Fill Question Title @1
Fill in the blanks:
The capital of France is [gap]Paris[/gap].
The capital of Germany is [gap]Berlin[/gap].

"""

TEMPLATE_CONTENT_WITH_EXAMPLES = """# TITLE: My Question Pool
# DESCRIPTION: A collection of questions for my ILIAS course

# ============================================================
# Question Syntax:
#   [t] - Question start marker (required)
#   [s] - Single choice question
#   [m] - Multiple choice question
#   [g] - Gap-fill question
#   _  - Correct answer (for MC questions)
#   -  - Incorrect answer (for MC questions)
#   [gap]content[/gap] - Gap to fill
#   @N - Points for the question (e.g., @2)
#
# Blank line required between questions!
# ============================================================

# ----------------------------------------------------------
# Example 1: Single Choice Question
# ----------------------------------------------------------
[t][s] What is the capital of France? @1
Which city is the capital of France?
- Berlin
- Madrid
_ Paris
- Rome

# ----------------------------------------------------------
# Example 2: Multiple Choice Question
# ----------------------------------------------------------
[t][m] Which programming languages are object-oriented? @2
Select all that apply.
- C
_ Python
_ Java
_ Assembly

# ----------------------------------------------------------
# Example 3: Gap-Fill Question
# ----------------------------------------------------------
[t][g] Fill in the missing words @2
Python is a [gap]high-level[/gap] programming language.
It supports [gap]multiple[/gap] programming paradigms.

# ----------------------------------------------------------
# Your questions go below:
# ----------------------------------------------------------

"""


def generate_template(output_path: str | Path, include_examples: bool = True) -> Path:
    """Generate a template question file.

    Parameters
    ----------
    output_path:
        Path where the template file will be created.
    include_examples:
        If True, include example questions demonstrating each type.
        If False, only include the syntax reference.

    Returns
    -------
    Path
        Path to the created template file.

    Raises
    ------
    FileExistsError
        If the output file already exists.
    """
    output_path = Path(output_path)

    if output_path.exists():
        raise FileExistsError(f"Template file already exists: {output_path}")

    content = TEMPLATE_CONTENT_WITH_EXAMPLES if include_examples else TEMPLATE_CONTENT_BASIC

    output_path.write_text(content, encoding="utf-8")
    return output_path
