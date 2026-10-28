# Agent Documentation for iliasqc

## Project Overview

`iliasqc` is a Python package that converts structured text files into ILIAS-compatible question pool and quiz zip archives. It supports single/multiple choice and gap-fill question types, generates QTI 1.2 compliant XML, and provides automated quiz combination generation to create balanced quizzes from multiple pools.

This project is based on [Kaffeedrache/Tiqi](https://github.com/Kaffeedrache/Tiqi).

## Package Structure

```
src/iliasqc/
├── __init__.py      # Package exports and version
├── cli.py           # Command-line interface (argparse, subcommands)
├── combine.py       # Quiz combination generator (pools, find combos, generate quiz from combo)
├── convert.py       # High-level conversion API (txt_to_zip, txt_to_qti, txt_to_quiz_zip)
├── ilias.py         # ILIAS question pool archive creation (manifest, export XML, zip building)
├── parser.py        # Question text file parser (Question, Answer dataclasses)
├── qti.py           # QTI 1.2 XML converter (question-to-XML rendering)
├── quiz.py          # ILIAS quiz/test archive creation (tst structure, integrated quiz)
└── template.py      # Question file template generator
```

Source lives in `src/iliasqc/`. The `build/lib/iliasqc/` directory is a build artifact and should not be edited.

## Question Text Format

Questions are defined in `.txt` files with special syntax:

```
# TITLE: My Question Pool
# DESCRIPTION: A collection of questions

[t][s] Single Choice Question Title @1
Question text goes here.
_ Correct answer
- Incorrect answer
- Another wrong answer

[t][m] Multiple Choice Question Title @2
Which options are correct?
- Wrong answer
_ Correct answer 1
_ Another correct answer
- Wrong again

[t][g] Gap-Fill Question Title @1
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

**Note:** Blank lines separate questions. Blank lines at the end of a file will cause issues if questions follow.

## CLI Commands

### `convert` — Question Pool Archive

```bash
iliasqc convert <input.txt> [-o output.zip] [-t "Title"] [-d "Description"] [-p 2]
```

Converts a question file into an ILIAS question **pool** zip archive. The pool uses references to external questions — the questions are NOT embedded.

### `qti` — QTI XML Export

```bash
iliasqc qti <input.txt> [-o output.xml] [-p 2]
```

Converts a question file to QTI XML only (no zip archive). Useful for debugging XML output.

### `template` — Template Generator

```bash
iliasqc template [-o output.txt] [--no-examples]
```

Generates a question file template with example questions (by default) or a minimal reference.

### `quiz` — Quiz (Test) Archive

```bash
iliasqc quiz <input.txt> [-o output.zip] [-t "Title"] [-d "Description"] [-p 2]
```

Converts a question file into an ILIAS quiz/test zip archive. Unlike `convert`, this creates an **integrated** quiz where questions are embedded directly in the QTI file (not pool references). The QTI content is wrapped in `<assessment>` and `<section>` elements.

### `combine` — Quiz Combination Generator

```bash
iliasqc combine <input.txt> -t <target_points> [-o output_dir] [-c max_combinations] [--csv-only] [--generate-quiz N]
```

The most complex command. It:
1. Generates separate pool zip files for each distinct point value in the input (e.g., 1pt pool, 2pt pool, 5pt pool).
2. Uses backtracking to find all valid combinations of pools that sum to the target points.
3. Ranks combinations by "balance score" (more diverse = lower score).
4. Exports a CSV with the combinations.
5. Optionally generates a quiz from a selected combination (`--generate-quiz N`), writing questions to a temp .txt file and feeding it through `txt_to_quiz_zip`.

## Architecture

### Data Flow

```
input.txt
    │
    ▼
parser.py          →  list[Question]  (parsed questions with type, text, answers, points)
    │
    ├──► qti.py             →  QTI XML string (questestinterop with item elements)
    │       │
    │       ├──► ilias.py:create_ilias_archive()   →  Pool zip archive (QPL + QTI)
    │       │
    │       └──► quiz.py:create_integrated_quiz_archive() →  Quiz zip archive (TST + embedded QTI)
    │
    └──► combine.py
            generate_pools_by_points() →  list[PoolInfo] (separate pools per point value)
            find_combinations()        →  list[PoolCombination] (balanced combos)
            generate_quiz_from_combination() →  quiz zip (writes temp .txt, feeds to txt_to_quiz_zip)
```

### Key Modules

**`parser.py`** — Core parsing logic. Creates `Question` and `Answer` dataclasses.
- `QUESTION_TYPE_MC_SINGLE = "SINGLE CHOICE QUESTION"`
- `QUESTION_TYPE_MC_MULTI = "MULTIPLE CHOICE QUESTION"`
- `QUESTION_TYPE_GAP = "CLOZE QUESTION"`
- Question IDs are generated as `il_1600_qst_{line_no}`
- `_parse_mc_answers` splits text on `<br/>` and looks for `_ ` / `- ` prefixes
- `_parse_gap_text` replaces `[gap]...[/gap]` markers with `<br/>` separators

**`qti.py`** — QTI 1.2 XML generation.
- Uses `ims_qtiasiv1p2p1.dtd`
- Single choice: correct answer gets all `points`, incorrect gets `0`
- Multiple choice: each correct answer gets `points / num_answers`, incorrect gets `points / num_answers`
- Gap-fill: points split evenly across gaps (last gap absorbs remainder)
- `_escape_xml` and `_escape_xml_attr` handle XML escaping

**`ilias.py`** — Question pool archive creation (QPL format).
- Creates a folder `{timestamp}__{nic}__qpl_{id}/` inside a zip
- Contains: QPL manifest (Questionpool_Test), QTI content, export.xml files
- `create_manifest` generates the QPL manifest with ILIAS CO DTD
- `create_manifest_file` generates the zip's root manifest.xml
- NIC defaults to `"1600"` (Network Installation Code)
- `export_target_point_combinations_csv` — curates balanced combinations with backtracking
- `update_pool_overview_csv` — maintains pool overview CSV

**`quiz.py`** — Quiz/test archive creation (TST format).
- `create_quiz_archive` — references external pool zip files (not embedded)
- `create_integrated_quiz_archive` — embeds questions directly in QTI (wrapped in `<assessment>/<section>`)
- `_wrap_qti_in_assessment` — wraps raw QTI items in assessment + section elements
- Uses `Entity="tst"` (not `"qpl"`) in export XML
- Includes Services/MediaObjects, Modules/File, Services/Object export components

**`combine.py`** — Combination generation.
- `PoolInfo` — metadata about a generated pool
- `PoolCombination` — a valid combination of pools (dict of pool_name → count)
- Backtracking algorithm to find combos summing to target (uses `Fraction` for precision)
- `balance_score` — lower is better (prefer more diverse combos)
- `generate_quiz_from_combination` — writes a temp .txt file, calls `txt_to_quiz_zip`

**`convert.py`** — High-level API.
- `txt_to_zip()` — converts to pool archive (uses `create_ilias_archive`)
- `txt_to_qti()` — converts to QTI XML only
- `txt_to_quiz_zip()` — converts to integrated quiz archive (uses `create_integrated_quiz_archive`)
- Supports `filter_points`, `title`/`description` overrides, custom output path

### Key Design Decisions

- **No external dependencies** — standard library only
- **Output compatible with ILIAS import** — QTI 1.2, manifest with ILIAS CO DTD
- **NIC defaults to `"1600"`** — Network Installation Code for tiqi compatibility
- **PCID and TriggerQuestion use qpl_id** (not question ID) for tiqi compatibility
- **QPL file** contains manifest XML, **QTI file** contains question content
- **Question IDs** generated from line numbers: `il_1600_qst_{line_no}`
- **Deterministic IDs/timestamps** — generated from SHA-1 hash of content for reproducibility

## tiqi Compatibility

Tests in `tests/test_ilias.py::TestTiqiParity` verify:
- Manifest uses ILIAS CO DTD format (`http://www.ilias.uni-koeln.de/download/dtd/ilias_co.dtd`)
- PCID uses qpl_id (not question ID)
- TriggerQuestion Id uses qpl_id
- Archive uses NIC 1600
- QPL file contains manifest XML (Questionpool_Test), NOT QTI content
- QTI file contains question content (questestinterop), NOT manifest

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

**Always run formatting and linting at the end of development before committing.**

### Test File Overview

| File | Tests |
|------|-------|
| `test_parser.py` | Question/Answer parsing, metadata extraction, point value extraction |
| `test_qti.py` | Question-to-XML rendering, escape handling, response processing |
| `test_ilias.py` | Pool manifest, export XML, zip structure, tiqi parity, CSV helpers |
| `test_quiz.py` | Test manifest, integrated quiz archive, assessment wrapping |
| `test_convert.py` | High-level API (txt_to_zip, txt_to_qti, txt_to_quiz_zip) |
| `test_combine.py` | Pool generation, combination finding, CSV export, table formatting, full pipeline |
| `test_cli.py` | All CLI subcommands, flags, error handling |
| `test_template.py` | Template generation with/without examples, file-exists guard |

### Writing New Tests

1. Use `tmp_path` (pytest fixture) for temporary directories.
2. Write minimal `.txt` content strings with proper blank-line separation.
3. For zip-based tests, always open with `zipfile.ZipFile(result)` and inspect `namelist()`.
4. Match zip file patterns by filename prefix (e.g., `qpl_`, `tst_`, `qti_`) — use `n.count("/") == 1` to check root-level files.
5. Use `capsys` for CLI tests that need to check stdout/stderr.

## Common Patterns

### Creating a Zip File for Testing

```python
import zipfile

pool_zip = tmp_path / "pool1.zip"
with zipfile.ZipFile(pool_zip, "w") as zf:
    zf.writestr("test.xml", qti_content)
```

### Inspecting Zip Contents

```python
with zipfile.ZipFile(output) as zf:
    names = zf.namelist()
    # Find specific files
    qti_file = [n for n in names if "qti_" in n and n.endswith(".xml")][0]
    content = zf.read(qti_file).decode("utf-8")
```

### CLI Testing

```python
content = "# TITLE: Test\n[t][s] Q @1\n_ A\n- B\n"
input_file = tmp_path / "questions.txt"
input_file.write_text(content)
result = main(["convert", str(input_file)])
assert result == 0
```

## File Path Conventions

| File | Purpose |
|------|---------|
| `src/iliasqc/*.py` | Source code — **edit these** |
| `build/lib/iliasqc/*.py` | Build artifacts — do NOT edit |
| `tests/test_*.py` | Tests |
| `pyproject.toml` | Project metadata, dependencies, tool configs |
| `README.md` | Public documentation |

## Version

Current version: **0.1.1** (from `pyproject.toml`).
