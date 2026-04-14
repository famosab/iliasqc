"""Tests for iliasqc.template."""

import pytest

from iliasqc.template import generate_template


def test_generate_template_with_examples(tmp_path):
    """Should create template with example questions."""
    output_path = tmp_path / "template.txt"
    result = generate_template(output_path, include_examples=True)

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text()
    assert "# TITLE:" in content
    assert "# DESCRIPTION:" in content
    assert "[t][s]" in content
    assert "[t][m]" in content
    assert "[t][g]" in content


def test_generate_template_without_examples(tmp_path):
    """Should create template without example questions."""
    output_path = tmp_path / "template.txt"
    result = generate_template(output_path, include_examples=False)

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text()
    assert "# TITLE:" in content
    assert "# DESCRIPTION:" in content


def test_template_raises_on_existing_file(tmp_path):
    """Should raise FileExistsError if template already exists."""
    output_path = tmp_path / "template.txt"
    output_path.write_text("existing content")

    with pytest.raises(FileExistsError):
        generate_template(output_path)
