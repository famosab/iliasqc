"""High-level conversion API for iliasqc."""

from __future__ import annotations

from pathlib import Path

from iliasqc.ilias import create_ilias_archive
from iliasqc.parser import extract_metadata, parse_question_file
from iliasqc.qti import convert_to_qti


def txt_to_zip(
    input_path: str | Path,
    output_path: str | Path | None = None,
    title: str | None = None,
    description: str | None = None,
    filter_points: float | None = None,
    unique_id: str | None = None,
    folder_timestamp: str | None = None,
) -> Path:
    """Convert a question text file to an ILIAS-compatible zip archive.

    Parameters
    ----------
    input_path:
        Path to the input ``.txt`` file containing the questions.
    output_path:
        Destination for the resulting ``.zip`` file. When ``None`` the zip is
        placed next to the input file with the same stem.
    title:
        Override for the pool title. If not provided, extracted from the
        ``# TITLE:`` comment in the input file or the filename.
    description:
        Override for the pool description. If not provided, extracted from
        the ``# DESCRIPTION:`` comment in the input file.
    filter_points:
        If provided, only include questions with this point value.

    Returns
    -------
    Path
        Absolute path of the created zip archive.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    ValueError
        If no questions are found in the file.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".zip")
    output_path = Path(output_path)

    if title is None or description is None:
        extracted_title, extracted_desc = extract_metadata(input_path)
        if title is None:
            title = extracted_title
        if description is None:
            description = extracted_desc

    questions = parse_question_file(input_path)

    if not questions:
        raise ValueError("No questions found in the input file.")

    if filter_points is not None:
        questions = [q for q in questions if q.points == filter_points]
        if not questions:
            raise ValueError(f"No questions found with {filter_points} points.")

    qti_content = convert_to_qti(questions)

    output_dir = output_path.parent
    if unique_id is None:
        unique_id = str(6599700 + int(questions[0].points if questions else 1))
    question_ids = [q.question_id for q in questions]

    archive_path = create_ilias_archive(
        qti_content,
        output_dir,
        title,
        description or "",
        unique_id=unique_id,
        question_ids=question_ids,
        folder_timestamp=folder_timestamp,
    )

    if output_path != archive_path:
        if output_path.exists():
            output_path.unlink()
        archive_path.rename(output_path)
        return output_path.resolve()

    return archive_path.resolve()


def txt_to_qti(
    input_path: str | Path,
    output_path: str | Path | None = None,
    filter_points: float | None = None,
) -> Path:
    """Convert a question text file to QTI XML format.

    Parameters
    ----------
    input_path:
        Path to the input ``.txt`` file containing the questions.
    output_path:
        Destination for the resulting ``.xml`` file. When ``None`` the XML is
        placed next to the input file with the same stem.
    filter_points:
        If provided, only include questions with this point value.

    Returns
    -------
    Path
        Absolute path of the created QTI XML file.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    ValueError
        If no questions are found in the file.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".xml")
    output_path = Path(output_path)

    questions = parse_question_file(input_path)

    if not questions:
        raise ValueError("No questions found in the input file.")

    if filter_points is not None:
        questions = [q for q in questions if q.points == filter_points]
        if not questions:
            raise ValueError(f"No questions found with {filter_points} points.")

    qti_content = convert_to_qti(questions)
    output_path.write_text(qti_content, encoding="utf-8")

    return output_path.resolve()
