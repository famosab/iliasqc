"""Tests for iliasqc.parser."""

from pathlib import Path

import pytest

from iliasqc.parser import (
    Answer,
    Question,
    extract_metadata,
    extract_point_values,
    parse_question_file,
    QUESTION_TYPE_GAP,
    QUESTION_TYPE_MC_MULTI,
    QUESTION_TYPE_MC_SINGLE,
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
