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

## Core Classes and Functions

### parser.py
- `Question` - Dataclass representing a parsed question
- `Answer` - Dataclass representing an MC answer option
- `parse_question_file(file_path)` - Parse a question text file
- `extract_point_values(file_path)` - Extract unique point values
- `extract_metadata(file_path)` - Extract title/description

### qti.py
- `create_question(question)` - Create QTI XML for a single question
- `convert_to_qti(questions)` - Convert all questions to QTI XML
- XML templates for QTI 1.2 format

### ilias.py
- `create_manifest(qpl_id, title, description, qti_id)` - Create ILIAS manifest XML
- `create_ilias_archive(...)` - Create ILIAS zip archive
- `update_pool_overview_csv(...)` - Update pool overview CSV
- `export_target_point_combinations_csv(...)` - Export quiz combinations (legacy)

### combine.py
- `PoolInfo` - Dataclass with pool metadata (name, filename, question count, points)
- `PoolCombination` - Dataclass with combination data and balance score
- `generate_pools_by_points(input_path, output_dir)` - Generate separate pools per point value
- `find_combinations(pools, target_points, max_combinations)` - Find balanced combinations
- `export_combinations_csv(output_dir, combinations, target_points)` - Export to CSV
- `format_combinations_table(combinations, pools, target_points)` - Human-readable table
- `generate_quiz_combinations(input_path, target_points, output_dir)` - Full pipeline

### template.py
- `generate_template(output_path, include_examples=True)` - Generate template file

### convert.py
- `txt_to_zip(input_path, output_path=None, title=None, description=None, filter_points=None)` - Convert to ILIAS zip
- `txt_to_qti(input_path, output_path=None, filter_points=None)` - Convert to QTI XML only

### cli.py
Commands:
- `convert` - Convert question file to ILIAS zip
- `qti` - Export QTI XML only
- `template` - Generate question template
- `combine` - Generate pools and find quiz combinations

## Continuous Integration (CI)

The project uses GitHub Actions for automated testing on every push and pull request.

### Workflow Files
- `.github/workflows/tests.yml` - Main CI workflow (test, lint, build)
- `.github/workflows/release-please.yml` - Automated releases
- `.github/dependabot.yml` - Automatic dependency updates

### CI Pipeline

The CI pipeline runs three jobs:

1. **test** - Runs pytest on Python 3.12, 3.13, 3.14
   - Installs package with dev dependencies
   - Runs tests with verbose output
   - Generates coverage report

2. **lint** - Code quality checks
   - Runs ruff linter
   - Checks code formatting

3. **build** - Package build verification
   - Builds the package with `python -m build`
   - Verifies build artifacts exist

### Automated Releases (release-please)

The project uses [release-please](https://github.com/googleapis/release-please) for automated versioning and releases:

- Monitors the `main` branch for conventional commits
- Automatically bumps version based on commit types (feat, fix, etc.)
- Creates release PRs and publishes to PyPI on merge
- Supports semantic versioning with changelog generation

### Dependency Updates (Dependabot)

The project uses [Dependabot](https://github.com/dependabot) for automatic dependency updates:

- Updates pip dependencies weekly
- Creates PRs with version updates
- Categorizes changes (features, fixes, maintenance)

### CI Configuration

The CI is configured in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.ruff]
line-length = 100
target-version = "py312"
```

## Future Development Ideas

1. **Additional Question Types**
   - True/False questions
   - Matching questions
   - Ordering questions
   - Essay/Numeric questions

2. **Import Functionality**
   - Import questions from ILIAS QTI XML export
   - Import from other formats (Moodle XML, Aiken format)

3. **Enhanced Features**
   - Question randomization/shuffling options
   - Image/media embedding support
   - LaTeX/MathML support for equations
   - Bulk processing with configuration files
   - Question tagging and categorization

4. **Validation & Quality**
   - Question validation (syntax, point consistency)
   - Duplicate detection
   - Accessibility checks

5. **ILIAS Integration**
   - Direct ILIAS API integration
   - Test/Quiz generation (not just pools)
   - Support for newer ILIAS versions

6. **CLI Enhancements**
   - Interactive question creation mode
   - Dry-run/preview mode
   - Configurable output templates

## Dependencies

- Python 3.12+
- Standard library only (no external dependencies at runtime)
- Dev: pytest, pytest-cov, ruff

## Key Design Decisions

- Use QTI 1.2 format for maximum ILIAS compatibility
- Keep dependencies minimal (standard library only)
- Support both CLI and Python API usage
- Deterministic output (SHA1-based IDs from content)
- Balance combinations by minimizing score variance across pool types

## Testing

Run tests locally with:
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
ruff format --check src/ tests/
```

## Building

```bash
pip install -e ".[dev]"
```

## Releasing

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag
4. Publish to PyPI: `python -m build && twine upload dist/*`
5. Update conda-forge recipe in `recipe/` directory
