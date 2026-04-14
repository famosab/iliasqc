"""Tests for iliasqc.cli."""

import pytest

from iliasqc.cli import main


class TestCliMain:
    """Tests for main function."""

    def test_convert_command(self, tmp_path, capsys):
        """convert subcommand should create zip archive."""
        from pathlib import Path

        content = """# TITLE: Test Pool
        [t][s] Question @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = main(["convert", str(input_file)])

        assert result == 0
        output = capsys.readouterr().out
        assert "Created:" in output
        assert str(tmp_path) in output or ".zip" in output

    def test_qti_command(self, tmp_path, capsys):
        """qti subcommand should create XML file."""
        from pathlib import Path

        content = """[t][s] Question @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = main(["qti", str(input_file)])

        assert result == 0
        output = capsys.readouterr().out
        assert "Created:" in output

    def test_template_command(self, tmp_path, capsys):
        """template subcommand should create template file."""
        from pathlib import Path

        output_file = tmp_path / "template.txt"
        result = main(["template", "-o", str(output_file)])

        assert result == 0
        assert output_file.exists()
        output = capsys.readouterr().out
        assert "Created template:" in output

    def test_template_no_examples(self, tmp_path, capsys):
        """template should create minimal template without examples."""
        from pathlib import Path

        output_file = tmp_path / "template.txt"
        result = main(["template", "-o", str(output_file), "--no-examples"])

        assert result == 0
        content = output_file.read_text()
        assert "[t][s]" in content

    def test_missing_input_returns_error(self, capsys):
        """Should return error for missing input file."""
        result = main(["convert", "/nonexistent/file.txt"])

        assert result == 1
        output = capsys.readouterr().err
        assert "Error:" in output

    def test_template_exists_returns_error(self, tmp_path, capsys):
        """Should return error if template already exists."""
        from pathlib import Path

        output_file = tmp_path / "template.txt"
        output_file.write_text("existing")

        result = main(["template", "-o", str(output_file)])

        assert result == 1
        output = capsys.readouterr().err
        assert "Error:" in output
