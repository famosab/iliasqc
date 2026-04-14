# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-04-14)


### Features

* add first version of the iliasqc package ([#2](https://github.com/famosab/iliasqc/issues/2)) ([46c0e68](https://github.com/famosab/iliasqc/commit/46c0e68aff14cd7be8a702d38abcf0f4aa0decd3))


### Bug Fixes

* add PAT ([813169b](https://github.com/famosab/iliasqc/commit/813169b42038e5d96f3ba3acbb8750f66f76cef6))
* move PAT token ([ea0fca4](https://github.com/famosab/iliasqc/commit/ea0fca4f66616707fccbd402a019af1865e0b903))

## [Unreleased]

## [0.1.0] - 2026-04-14

### Added
- Initial package structure with `pyproject.toml` for pip compatibility.
- `src/iliasqc/convert.py` with `txt_to_zip` function.
- `src/iliasqc/cli.py` with `iliasqc` command-line entry point.
- `recipe/meta.yaml` conda-forge recipe template.
- Basic test suite in `tests/`.
