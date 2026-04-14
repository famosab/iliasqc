"""Tests for iliasqc.cli."""

from iliasqc import __version__
from iliasqc.cli import main


class TestCliMain:
    """Tests for main function."""

    def test_convert_command(self, tmp_path, capsys):
        """convert subcommand should create zip archive."""

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

        output_file = tmp_path / "template.txt"
        result = main(["template", "-o", str(output_file)])

        assert result == 0
        assert output_file.exists()
        output = capsys.readouterr().out
        assert "Created template:" in output

    def test_template_no_examples(self, tmp_path, capsys):
        """template should create minimal template without examples."""

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

        output_file = tmp_path / "template.txt"
        output_file.write_text("existing")

        result = main(["template", "-o", str(output_file)])

        assert result == 1
        output = capsys.readouterr().err
        assert "Error:" in output

    def test_convert_with_title_flag(self, tmp_path, capsys):
        """convert should accept -t / --title flag."""

        content = """# TITLE: Test
        [t][s] Question @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = main(["convert", str(input_file), "-t", "Custom Title"])
        assert result == 0

        result = main(["convert", str(input_file), "--title", "Another Title"])
        assert result == 0

    def test_combine_with_target_flag(self, tmp_path, capsys):
        """combine should require -t / --target flag."""

        content = """# TITLE: Test
        [t][s] Q1 @1
        _ A
        - B

        [t][s] Q2 @1
        _ C
        - D
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = main(["combine", str(input_file), "-t", "2"])
        assert result == 0

        result = main(["combine", str(input_file), "--target", "2"])
        assert result == 0

    def test_combine_without_target_fails(self, tmp_path, capsys):
        """combine should fail without --target flag."""

        content = """# TITLE: Test
        [t][s] Q1 @1
        _ A
        - B
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        result = main(["combine", str(input_file)])
        assert result == 1
        output = capsys.readouterr().err
        assert "--target" in output

    def test_version_flag_outputs_version(self, capsys):
        """--version should print CLI version and exit."""
        exit_code = None
        try:
            main(["--version"])
        except SystemExit as exc:
            exit_code = exc.code

        assert exit_code == 0
        output = capsys.readouterr().out
        assert __version__ in output

    def test_help_includes_version(self, capsys):
        """--help output should include the current version."""
        exit_code = None
        try:
            main(["--help"])
        except SystemExit as exc:
            exit_code = exc.code

        assert exit_code == 0
        output = capsys.readouterr().out
        assert __version__ in output
