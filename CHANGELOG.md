# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1](https://github.com/famosab/iliasqc/compare/v0.1.0...v0.1.1) (2026-04-14)


### Bug Fixes

* change zip structure for validation upon Ilias upload ([#8](https://github.com/famosab/iliasqc/issues/8)) ([8751360](https://github.com/famosab/iliasqc/commit/87513601dd8d02a4f953fbbe2de5480d36ef0be4))
* create valid zip ([#5](https://github.com/famosab/iliasqc/issues/5)) ([77afee6](https://github.com/famosab/iliasqc/commit/77afee6eb97b488abea126ca18c7feae54fc6704))

## 0.1.0 (2026-04-14)


### Features

* add first version of the iliasqc package ([#2](https://github.com/famosab/iliasqc/issues/2)) ([46c0e68](https://github.com/famosab/iliasqc/commit/46c0e68aff14cd7be8a702d38abcf0f4aa0decd3))


### Bug Fixes

* add PAT ([813169b](https://github.com/famosab/iliasqc/commit/813169b42038e5d96f3ba3acbb8750f66f76cef6))
* move PAT token ([ea0fca4](https://github.com/famosab/iliasqc/commit/ea0fca4f66616707fccbd402a019af1865e0b903))

## [Unreleased]

### Added

- Quiz combination generation feature (generate pools per point value, find combinations)
- `iliasqc combine` CLI command with `--generate-quiz` option
- `generate_quiz_from_combination()` function to create quiz from pool combination
- Quiz archive generation (`create_quiz_archive`, `create_integrated_quiz_archive`)
- `txt_to_quiz_zip()` function for CLI `quiz` command
- Pool overview and target point combination CSV functions
- `convert_to_qti()` function for programmatic QTI conversion

## [0.1.0] - 2026-04-14

### Added
- Initial package structure with `pyproject.toml` for pip compatibility.
- `src/iliasqc/convert.py` with `txt_to_zip` function.
- `src/iliasqc/cli.py` with `iliasqc` command-line entry point.
- `recipe/meta.yaml` conda-forge recipe template.
- Basic test suite in `tests/`.
