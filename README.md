# iliasqc

[![PyPI version](https://img.shields.io/pypi/v/iliasqc.svg)](https://pypi.org/project/iliasqc/)
[![conda-forge version](https://img.shields.io/conda/vn/conda-forge/iliasqc.svg)](https://anaconda.org/conda-forge/iliasqc)
[![Tests](https://github.com/famosab/iliasqc/actions/workflows/tests.yml/badge.svg)](https://github.com/famosab/iliasqc/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-025e8a?logo=dependabot)](https://github.com/famosab/iliasqc/security/dependabot)

Python package to convert structured text files into ILIAS-compatible question pool zip archives. Supports single/multiple choice and gap-fill question types, plus automated quiz combination generation.

## Features

- **Multiple question types**: Single choice, multiple choice, and gap-fill questions
- **QTI 1.2 compliant**: Generates ILIAS-compatible XML format
- **Python API**: Use programmatically in your Python code
- **CLI tool**: Convert files from the command line
- **Template generator**: Create question file templates with examples
- **Quiz combinations**: Generate multiple pools and find optimal combinations to reach target point totals

## Installation

### pip

```bash
pip install iliasqc
```

### conda / mamba (conda-forge)

```bash
conda install -c conda-forge iliasqc
# or
mamba install -c conda-forge iliasqc
```

## Question File Format

Questions are defined in `.txt` files with special syntax:

```
# TITLE: My Question Pool
# DESCRIPTION: A collection of questions

[t][s] Single Choice Question @1
Question text goes here.
_ Correct answer
- Incorrect answer
- Another wrong answer

[t][m] Multiple Choice Question @2
Which options are correct?
- Wrong answer
_ Correct answer 1
_ Correct answer 2
- Wrong again

[t][g] Gap-Fill Question @1
The capital of France is [gap]Paris[/gap].
The capital of Germany is [gap]Berlin[/gap].
```

### Syntax Reference

| Marker | Description |
|--------|-------------|
| `[t]` | Question start marker (required) |
| `[s]` | Single choice question |
| `[m]` | Multiple choice question |
| `[g]` | Gap-fill question |
| `_` | Correct answer (for MC questions) |
| `-` | Incorrect answer (for MC questions) |
| `[gap]...[/gap]` | Gap to fill |
| `@N` | Points for the question (e.g., `@2`) |
| `# TITLE:` | Pool title metadata |
| `# DESCRIPTION:` | Pool description metadata |

## Usage

### Command Line

Convert a question file to ILIAS zip archive:

```bash
iliasqc convert questions.txt
```

Specify custom output path:

```bash
iliasqc convert questions.txt -o my_pool.zip
```

Override title and description:

```bash
iliasqc convert questions.txt -t "My Pool" --description "My description"
```

Filter questions by point value:

```bash
iliasqc convert questions.txt -p 2
```

#### Quiz Combinations

Generate multiple pools (one per point value) and find combinations to reach a target:

```bash
iliasqc combine questions.txt -t 20
```

This will:
1. Create separate zip files for each point value found in your questions
2. Find all valid combinations that sum to 20 points
3. Display a table showing the combinations ranked by balance
4. Export a CSV file with the combinations

Options:
- `-t, --target`: Target total points (required)
- `-o, --output`: Output directory (default: same as input file)
- `-c, --combinations`: Maximum number of combinations to show (default: 10)
- `--csv-only`: Only output CSV, skip the table display

Example output:
```
Quiz Combinations for 20.0 Points
======================================================================

Available Pools:
  - My Pool (5 points): 8 questions
  - My Pool (4 points): 12 questions
  - My Pool (2 points): 15 questions

──────────────────────────────────────────────────────────────────────
Rank  Questions  Balance  Combination
──────────────────────────────────────────────────────────────────────

1     5          ●●●●     2x My Pool (5 points) + 5x My Pool (2 points)
2     4          ●●●○     5x My Pool (4 points)
3     6          ●●●○     3x My Pool (4 points) + 5x My Pool (2 points)
──────────────────────────────────────────────────────────────────────

Tip: Lower balance score = more diverse quiz

Generated 3 pools:
  - My Pool_2pt_pool.zip: 15 questions
  - My Pool_4pt_pool.zip: 12 questions
  - My Pool_5pt_pool.zip: 8 questions
```

Export as QTI XML (without creating zip archive):

```bash
iliasqc qti questions.txt -o output.xml
```

Generate a question template file:

```bash
iliasqc template -o my_template.txt
```

Generate template without examples:

```bash
iliasqc template -o basic_template.txt --no-examples
```

### Python API

```python
from iliasqc import txt_to_zip, txt_to_qti, generate_template

# Convert to ILIAS zip archive
output_path = txt_to_zip("questions.txt")
print(f"Created: {output_path}")

# Convert to QTI XML only
xml_path = txt_to_qti("questions.txt", "output.xml")
print(f"Created: {xml_path}")

# Generate a template
template_path = generate_template("my_template.txt")
print(f"Created template: {template_path}")
```

#### Quiz Combination API

```python
from iliasqc import (
    generate_quiz_combinations,
    generate_pools_by_points,
    find_combinations,
    format_combinations_table,
    export_combinations_csv,
)

# Generate pools and find combinations (full pipeline)
pools, combinations = generate_quiz_combinations(
    "questions.txt",
    target_points=20,
    output_dir=".",
)

# Or use individual functions
pools = generate_pools_by_points("questions.txt")
combinations = find_combinations(pools, target_points=20)

# Format as a text table
table = format_combinations_table(combinations, pools, target_points=20)
print(table)

# Export to CSV
csv_path = export_combinations_csv(".", combinations, target_points=20)
```

## Development

```bash
git clone https://github.com/famosab/iliasqc.git
cd iliasqc
pip install -e ".[dev]"
```

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=iliasqc --cov-report=term-missing
```

### Code Quality

Run linting checks:
```bash
ruff check src/ tests/
ruff format --check src/ tests/
```

Fix linting issues automatically:
```bash
ruff check --fix src/ tests/
ruff format src/ tests/
```

### Continuous Integration

The project uses GitHub Actions for automated testing. The CI pipeline runs on every push and pull request, testing against Python 3.12, 3.13, and 3.14.

## License

MIT – see [LICENSE](LICENSE).
