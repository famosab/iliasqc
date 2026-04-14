"""Tests for iliasqc.parser."""

from pathlib import Path

import pytest

from iliasqc.parser import (
    QUESTION_TYPE_GAP,
    QUESTION_TYPE_MC_MULTI,
    QUESTION_TYPE_MC_SINGLE,
    extract_metadata,
    extract_point_values,
    parse_question_file,
    validate_question_file,
)


class TestParseQuestionFile:
    """Tests for parse_question_file function."""

    def test_parses_single_choice_question(self, tmp_path: Path) -> None:
        """Single choice questions should be parsed correctly."""
        content = """[t][s] What is 2+2? @1
        The answer is 4.
        _ 4
        - 5
        - 3
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        questions = parse_question_file(input_file)

        assert len(questions) == 1
        assert questions[0].question_type == QUESTION_TYPE_MC_SINGLE
        assert questions[0].title == "What is 2+2?"
        assert questions[0].points == 1.0
        assert len(questions[0].answers) == 3
        assert questions[0].answers[0].text == "4"
        assert questions[0].answers[0].is_correct is True

    def test_parses_multiple_choice_question(self, tmp_path: Path) -> None:
        """Multiple choice questions should be parsed correctly."""
        content = """[t][m] Which are prime? @2
        Select all prime numbers.
        - 4
        _ 2
        _ 3
        - 6
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        questions = parse_question_file(input_file)

        assert len(questions) == 1
        assert questions[0].question_type == QUESTION_TYPE_MC_MULTI
        assert len(questions[0].answers) == 4
        assert questions[0].answers[0].is_correct is False
        assert questions[0].answers[1].is_correct is True
        assert questions[0].answers[2].is_correct is True

    def test_parses_gap_question(self, tmp_path: Path) -> None:
        """Gap-fill questions should be parsed correctly."""
        content = """[t][g] Fill in the blank @1
        The capital of France is [gap]Paris[/gap].
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        questions = parse_question_file(input_file)

        assert len(questions) == 1
        assert questions[0].question_type == QUESTION_TYPE_GAP
        assert "[gap]Paris[/gap]" in questions[0].text

    def test_parses_multiple_questions(self, tmp_path: Path) -> None:
        """Multiple questions should be parsed correctly."""
        content = """[t][s] Question 1 @1
        Answer 1.
        _ Correct
        - Wrong

        [t][m] Question 2 @2
        Answer 2.
        _ Correct
        - Wrong
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        questions = parse_question_file(input_file)

        assert len(questions) == 2
        assert questions[0].question_type == QUESTION_TYPE_MC_SINGLE
        assert questions[1].question_type == QUESTION_TYPE_MC_MULTI

    def test_ignores_comments(self, tmp_path: Path) -> None:
        """Lines starting with # should be ignored."""
        content = """# TITLE: Test Pool
        # DESCRIPTION: A test
        [t][s] Question @1
        _ Correct
        - Wrong
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        questions = parse_question_file(input_file)

        assert len(questions) == 1

    def test_raises_on_missing_file(self) -> None:
        """Should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_question_file("/nonexistent/file.txt")


class TestExtractMetadata:
    """Tests for extract_metadata function."""

    def test_extracts_title_and_description(self, tmp_path: Path) -> None:
        """Title and description should be extracted from file."""
        content = """# TITLE: My Pool
        # DESCRIPTION: A description
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        title, description = extract_metadata(input_file)

        assert title == "My Pool"
        assert description == "A description"

    def test_uses_filename_as_default_title(self, tmp_path: Path) -> None:
        """Filename should be used as default title."""
        content = """# DESCRIPTION: Some description
        """
        input_file = tmp_path / "my_questions.txt"
        input_file.write_text(content)

        title, description = extract_metadata(input_file)

        assert title == "my_questions"
        assert description == "Some description"


class TestExtractPointValues:
    """Tests for extract_point_values function."""

    def test_extracts_point_values(self, tmp_path: Path) -> None:
        """Point values should be extracted from questions."""
        content = """[t][s] Q1 @1
        _ A
        - B

        [t][s] Q2 @2
        _ A
        - B

        [t][s] Q3 @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        point_values = extract_point_values(input_file)

        assert point_values == [1.0, 2.0]

    def test_returns_default_for_no_points(self, tmp_path: Path) -> None:
        """Should return [1.0] when no points are specified."""
        content = """[t][s] Q1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        point_values = extract_point_values(input_file)

        assert point_values == [1.0]


class TestValidateQuestionFile:
    """Tests for validate_question_file function."""

    def test_valid_file_returns_true(self, tmp_path: Path) -> None:
        """Valid question file should pass validation."""
        content = """# TITLE: Test Pool

[t][m] What is 2+2? @1
_ 4
- 3

[t][s] What is 5+5? @2
_ 10
- 9
"""
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = validate_question_file(input_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_missing_file_returns_false(self) -> None:
        """Missing file should return validation error."""
        result = validate_question_file("/nonexistent/file.txt")

        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0].line_number == 0
        assert "not found" in result.errors[0].message

    def test_missing_answers_returns_error(self, tmp_path: Path) -> None:
        """Multiple choice question with no answers should fail."""
        content = "[t][m] Question without answers @1"
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = validate_question_file(input_file)

        assert result.valid is False
        assert len(result.errors) == 1
        assert "no answers" in result.errors[0].message.lower()

    def test_invalid_question_type_returns_error(self, tmp_path: Path) -> None:
        """Invalid question type marker should fail."""
        content = "[t][x] Invalid question @1"
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = validate_question_file(input_file)

        assert result.valid is False
        assert any("question type" in e.message.lower() for e in result.errors)

    def test_invalid_point_value_returns_error(self, tmp_path: Path) -> None:
        """Invalid point value should fail validation."""
        content = "[t][s] Question @invalid"
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = validate_question_file(input_file)

        assert result.valid is False
        assert any("point" in e.message.lower() for e in result.errors)

    def test_gap_in_multiple_choice_returns_error(self, tmp_path: Path) -> None:
        """Gap markers in multiple choice questions should fail."""
        content = """[t][m] Question
- Wrong
[gap]gap[/gap] text
"""
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = validate_question_file(input_file)

        assert result.valid is False
        assert any("gap" in e.message.lower() for e in result.errors)

    def test_gap_question_passes_validation(self, tmp_path: Path) -> None:
        """Gap-fill questions should pass validation."""
        content = """[t][g] Fill the blank @1
The answer is [gap]test[/gap].
"""
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = validate_question_file(input_file)

        assert result.valid is True
