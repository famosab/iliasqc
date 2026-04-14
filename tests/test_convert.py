"""Tests for iliasqc.convert."""

import zipfile
from pathlib import Path

import pytest

from iliasqc.convert import txt_to_zip


def test_txt_to_zip_creates_file(tmp_path: Path) -> None:
    """txt_to_zip should create a zip archive at the expected path."""
    input_file = tmp_path / "questions.txt"
    input_file.write_text("Sample question content.\n")

    output = txt_to_zip(input_file)

    assert output.exists()
    assert output.suffix == ".zip"


def test_txt_to_zip_contains_input(tmp_path: Path) -> None:
    """The zip archive should contain the original txt file."""
    input_file = tmp_path / "questions.txt"
    content = "Sample question content.\n"
    input_file.write_text(content)

    output = txt_to_zip(input_file)

    with zipfile.ZipFile(output) as zf:
        names = zf.namelist()
        assert "questions.txt" in names
        assert zf.read("questions.txt").decode() == content


def test_txt_to_zip_custom_output(tmp_path: Path) -> None:
    """txt_to_zip should respect an explicit output path."""
    input_file = tmp_path / "questions.txt"
    input_file.write_text("content\n")
    custom_output = tmp_path / "custom_output.zip"

    result = txt_to_zip(input_file, custom_output)

    assert result == custom_output.resolve()
    assert custom_output.exists()


def test_txt_to_zip_missing_input(tmp_path: Path) -> None:
    """txt_to_zip should raise FileNotFoundError for a missing input file."""
    with pytest.raises(FileNotFoundError):
        txt_to_zip(tmp_path / "nonexistent.txt")
