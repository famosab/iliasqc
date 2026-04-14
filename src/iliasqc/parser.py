"""Question text file parser for iliasqc."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Answer:
    """Represents an answer option for a multiple choice question."""

    text: str
    is_correct: bool


@dataclass
class Question:
    """Represents a parsed question."""

    question_type: str
    title: str
    text: str
    points: float = 1.0
    answers: list[Answer] = field(default_factory=list)
    line_number: int = 0
    question_id: str = ""


QUESTION_TYPE_MC_SINGLE = "assSingleChoice"
QUESTION_TYPE_MC_MULTI = "assMultipleChoice"
QUESTION_TYPE_GAP = "assClozeQuestion"


def extract_point_values(file_path: str | Path) -> list[float]:
    """Extract all unique point values from the input file.

    Parameters
    ----------
    file_path:
        Path to the question text file.

    Returns
    -------
    list[float]
        Sorted list of unique point values found in the file.
    """
    point_values: set[float] = set()
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[t]"):
                    title_with_points = line[3:].strip()
                    if "@" in title_with_points:
                        parts = title_with_points.rsplit("@", 1)
                        try:
                            points = float(parts[1].strip())
                            point_values.add(points)
                        except ValueError:
                            pass
    except Exception:
        pass

    return sorted(point_values) if point_values else [1.0]


def extract_metadata(file_path: str | Path) -> tuple[str, str]:
    """Extract title and description from input file.

    Parameters
    ----------
    file_path:
        Path to the question text file.

    Returns
    -------
    tuple[str, str]
        A tuple of (title, description). Title defaults to the filename
        without extension if not found in the file.
    """
    title = os.path.splitext(os.path.basename(file_path))[0]
    description = ""

    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# TITLE:"):
                    title = line[8:].strip()
                elif line.startswith("# DESCRIPTION:"):
                    description = line[14:].strip()
    except Exception:
        pass

    return title, description


def _parse_mc_answers(text: str) -> list[Answer]:
    """Parse multiple choice answers from question text.

    Parameters
    ----------
    text:
        The question text containing answer lines.

    Returns
    -------
    list[Answer]
        List of Answer objects parsed from the text.
    """
    answers: list[Answer] = []
    normalized = text.replace("<br/>", "\n")
    for line in normalized.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("_ "):
            answers.append(Answer(text=line[2:], is_correct=True))
        elif line.startswith("- "):
            answers.append(Answer(text=line[2:], is_correct=False))
    return answers


def _parse_gap_text(text: str) -> str:
    """Parse gap-fill question text, replacing gap markers with line breaks.

    Parameters
    ----------
    text:
        The question text with [gap][/gap] markers.

    Returns
    -------
    str
        The text with gaps represented as <br/> separators.
    """
    gap_re = r"\[gap\]([^\[\]]*)\[/gap\]"
    parts = re.split(gap_re, text)
    result_parts: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            result_parts.append(part)
        else:
            result_parts.append("<br/>")
    return "".join(result_parts)


def parse_question_file(file_path: str | Path) -> list[Question]:
    """Parse a question text file into Question objects.

    Parameters
    ----------
    file_path:
        Path to the question text file.

    Returns
    -------
    list[Question]
        List of parsed Question objects.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    questions: list[Question] = []
    current_question: Question | None = None
    current_text_lines: list[str] = []
    in_question = False

    with open(file_path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.rstrip("\n")
            stripped = line.strip()

            if stripped == "" and in_question:
                questions.append(current_question)
                current_question = None
                current_text_lines = []
                in_question = False
                continue

            if stripped == "":
                continue

            if stripped.startswith("#"):
                continue

            if stripped.startswith("[t]"):
                if current_question is not None:
                    questions.append(current_question)

                question_id = f"il_1600_qst_{line_no}"

                question_type = QUESTION_TYPE_MC_SINGLE
                if stripped[3:6] == "[s]":
                    question_type = QUESTION_TYPE_MC_SINGLE
                elif stripped[3:6] == "[m]":
                    question_type = QUESTION_TYPE_MC_MULTI
                elif stripped[3:6] == "[g]":
                    question_type = QUESTION_TYPE_GAP

                title_with_points = stripped[6:].strip()
                points = 1.0
                title = title_with_points

                if "@" in title_with_points:
                    parts = title_with_points.rsplit("@", 1)
                    title = parts[0].strip()
                    try:
                        points = float(parts[1].strip())
                    except ValueError:
                        title = title_with_points

                current_question = Question(
                    question_type=question_type,
                    title=title,
                    text="",
                    points=points,
                    line_number=line_no,
                    question_id=question_id,
                )
                in_question = True
                continue

            if in_question and current_question is not None:
                if current_text_lines:
                    current_text_lines.append("<br/>" + stripped)
                else:
                    current_text_lines.append(stripped)
                current_question.text = "".join(current_text_lines)

    if current_question is not None:
        if current_question.text:
            questions.append(current_question)

    for q in questions:
        if q.question_type in (QUESTION_TYPE_MC_SINGLE, QUESTION_TYPE_MC_MULTI):
            q.answers = _parse_mc_answers(q.text)

    return questions
