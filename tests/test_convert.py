"""Tests for iliasqc.convert."""

import zipfile
from pathlib import Path

import pytest

from iliasqc.convert import txt_to_qti, txt_to_quiz_zip, txt_to_zip


class TestTxtToZip:
    """Tests for txt_to_zip function."""

    def test_creates_zip_archive(self, tmp_path: Path) -> None:
        """Should create a valid ILIAS zip archive."""
        content = """# TITLE: Test Pool
        # DESCRIPTION: Test description
        [t][s] What is 2+2? @1
        _ 4
        - 5
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_zip(input_file)

        assert output.exists()
        assert output.suffix == ".zip"

    def test_zip_contains_ilias_structure(self, tmp_path: Path) -> None:
        """Zip should contain manifest and QTI files."""
        content = """# TITLE: Test Pool
        [t][s] Question @1
        _ Correct
        - Wrong
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_zip(input_file)

        with zipfile.ZipFile(output) as zf:
            names = zf.namelist()
            assert any("qpl_" in name for name in names)
            assert any("qti_" in name for name in names)

    def test_custom_output_path(self, tmp_path: Path) -> None:
        """Should respect custom output path."""
        content = """[t][s] Q @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)
        custom_output = tmp_path / "custom.zip"

        result = txt_to_zip(input_file, custom_output)

        assert result == custom_output.resolve()
        assert custom_output.exists()

    def test_custom_title_and_description(self, tmp_path: Path) -> None:
        """Should use custom title and description."""
        content = """# TITLE: Should be ignored
        [t][s] Q @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_zip(
            input_file,
            title="Custom Title",
            description="Custom Description",
        )

        assert output.exists()

    def test_filter_by_points(self, tmp_path: Path) -> None:
        """Should filter questions by point value."""
        content = """[t][s] Q1 @1
        _ A
        - B

        [t][s] Q2 @2
        _ C
        - D
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_zip(input_file, filter_points=1.0)

        assert output.exists()

        with zipfile.ZipFile(output) as zf:
            qti_content = None
            for name in zf.namelist():
                if "qti_" in name:
                    qti_content = zf.read(name).decode()
                    break

            assert qti_content is not None
            assert "Q1" in qti_content

    def test_missing_input_raises(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError for missing input."""
        with pytest.raises(FileNotFoundError):
            txt_to_zip(tmp_path / "nonexistent.txt")

    def test_no_questions_raises(self, tmp_path: Path) -> None:
        """Should raise ValueError for file with no questions."""
        input_file = tmp_path / "questions.txt"
        input_file.write_text("# Just a comment\n")

        with pytest.raises(ValueError, match="No questions found"):
            txt_to_zip(input_file)


class TestTxtToQti:
    """Tests for txt_to_qti function."""

    def test_creates_xml_file(self, tmp_path: Path) -> None:
        """Should create QTI XML file."""
        content = """[t][s] Question @1
        _ Correct
        - Wrong
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_qti(input_file)

        assert output.exists()
        assert output.suffix == ".xml"

    def test_xml_contains_questions(self, tmp_path: Path) -> None:
        """XML should contain question content."""
        content = """# TITLE: Test
        [t][s] Test Question @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_qti(input_file)

        content_text = output.read_text()
        assert "<questestinterop>" in content_text
        assert "Test Question" in content_text
        assert "</questestinterop>" in content_text

    def test_filter_by_points(self, tmp_path: Path) -> None:
        """Should filter questions by point value."""
        content = """[t][s] Keep @1
        _ A
        - B

        [t][s] Skip @2
        _ C
        - D
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_qti(input_file, filter_points=1.0)

        content_text = output.read_text()
        assert "Keep" in content_text
        assert "Skip" not in content_text

    def test_missing_input_raises(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError for missing input."""
        with pytest.raises(FileNotFoundError):
            txt_to_qti(tmp_path / "nonexistent.txt")


class TestTxtToQuizZip:
    """Tests for txt_to_quiz_zip function."""

    def test_creates_quiz_zip_archive(self, tmp_path: Path) -> None:
        """Should create a valid ILIAS quiz zip archive."""
        content = """# TITLE: Test Quiz
        # DESCRIPTION: Test description
        [t][s] What is 2+2? @1
        _ 4
        - 5
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_quiz_zip(input_file)

        assert output.exists()
        assert output.suffix == ".zip"

    def test_zip_contains_tst_structure(self, tmp_path: Path) -> None:
        """Quiz zip should contain test structure (not pool)."""
        content = """# TITLE: Test Quiz
        [t][s] Question @1
        _ Correct
        - Wrong
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_quiz_zip(input_file)

        with zipfile.ZipFile(output) as zf:
            names = zf.namelist()
            assert any("tst_" in name for name in names)
            assert any("qti_" in name for name in names)

    def test_custom_output_path(self, tmp_path: Path) -> None:
        """Should respect custom output path."""
        content = """[t][s] Q @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)
        custom_output = tmp_path / "custom_quiz.zip"

        result = txt_to_quiz_zip(input_file, custom_output)

        assert result == custom_output.resolve()
        assert custom_output.exists()

    def test_custom_title_and_description(self, tmp_path: Path) -> None:
        """Should use custom title and description."""
        content = """# TITLE: Should be ignored
        [t][s] Q @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_quiz_zip(
            input_file,
            title="Custom Quiz Title",
            description="Custom Quiz Description",
        )

        assert output.exists()

    def test_filter_by_points(self, tmp_path: Path) -> None:
        """Should filter questions by point value."""
        content = """[t][s] Q1 @1
        _ A
        - B

        [t][s] Q2 @2
        _ C
        - D
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        output = txt_to_quiz_zip(input_file, filter_points=1.0)

        assert output.exists()

    def test_missing_input_raises(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError for missing input."""
        with pytest.raises(FileNotFoundError):
            txt_to_quiz_zip(tmp_path / "nonexistent.txt")

    def test_no_questions_raises(self, tmp_path: Path) -> None:
        """Should raise ValueError for file with no questions."""
        input_file = tmp_path / "questions.txt"
        input_file.write_text("# Just a comment\n")

        with pytest.raises(ValueError, match="No questions found"):
            txt_to_quiz_zip(input_file)
