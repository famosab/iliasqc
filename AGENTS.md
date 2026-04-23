# Agent Documentation for iliasqc

## Project Overview

`iliasqc` is a Python package that converts structured text files into ILIAS-compatible question pool zip archives. It supports multiple question types (single/multiple choice, gap-fill) and generates QTI 1.2 compliant XML. It also provides quiz combination generation to create balanced quizzes from multiple pools.

## Package Structure

```
src/iliasqc/
├── __init__.py      # Package exports and version
├── cli.py           # Command-line interface
├── combine.py       # Quiz combination generator
├── convert.py       # High-level conversion API
├── ilias.py         # ILIAS archive creation
├── parser.py        # Question text file parser
├── qti.py           # QTI XML converter
└── template.py      # Template file generator
```

## Question Text Format

Questions are defined in `.txt` files with special syntax:

- `[t]` - Question start marker
- `[s]` - Single choice question
- `[m]` - Multiple choice question
- `[g]` - Gap-fill question
- `_` - Correct answer (MC questions)
- `-` - Incorrect answer (MC questions)
- `[gap]content[/gap]` - Gap to fill
- `@N` - Points for the question (e.g., `@2`)
- `# TITLE:` - Pool title metadata
- `# DESCRIPTION:` - Pool description metadata

Example:
```
# TITLE: My Question Pool
# DESCRIPTION: Sample questions for testing

[t][m] Multiple Choice Question @2
Which is correct?
- Wrong answer
_ Correct answer
- Another wrong
```

## CLI Commands

- `iliasqc convert <input.txt>` - Convert question file to ILIAS zip
- `iliasqc qti <input.txt>` - Export QTI XML only
- `iliasqc template` - Generate question template
- `iliasqc combine <input.txt> -t <target_points>` - Generate pools and find quiz combinations

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=iliasqc --cov-report=term-missing
```

Run linting:
```bash
ruff check src/ tests/
```

Run formatting:
```bash
ruff format --check src/ tests/
```

**Always run formatting and linting at the end of development to avoid errors in the CI/push pipeline.**

## Key Design Decisions

- Output format is compatible with ILIAS import (QTI 1.2, manifest with ILIAS CO DTD)
- NIC (Network Installation Code) defaults to "1600"
- PCID and TriggerQuestion use qpl_id for tiqi compatibility
- QPL file contains manifest XML, QTI file contains question content
- No external dependencies (standard library only)

## tiqi Compatibility

The package is designed to produce output compatible with tiqi.py. Tests in `test_ilias.py::TestTiqiParity` verify:
- Manifest uses ILIAS CO DTD format
- PCID and TriggerQuestion use pool ID (not question ID)
- Archive uses NIC 1600
- QPL file contains manifest, QTI file contains questions