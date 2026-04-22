"""Tests for iliasqc.qti."""

from iliasqc.parser import (
    QUESTION_TYPE_GAP,
    QUESTION_TYPE_MC_MULTI,
    QUESTION_TYPE_MC_SINGLE,
    Answer,
    Question,
)
from iliasqc.qti import convert_to_qti, create_question


class TestCreateQuestion:
    """Tests for create_question function."""

    def test_creates_gap_question_xml(self) -> None:
        """Gap questions should generate correct XML structure."""
        question = Question(
            question_type=QUESTION_TYPE_GAP,
            title="Test Gap",
            text="The answer is [gap]42[/gap].",
            points=1.0,
            line_number=1,
            question_id="q_1",
        )

        presentation, feedback, resprocessing = create_question(question)

        assert 'response_str ident="gap_0"' in presentation
        assert 'varequal respident="gap_0">42' in resprocessing
        assert 'setvar action="Add">1.0' in resprocessing
        assert "_Response_0" in feedback

    def test_creates_single_choice_question_xml(self) -> None:
        """Single choice questions should generate correct XML structure."""
        question = Question(
            question_type=QUESTION_TYPE_MC_SINGLE,
            title="Test MC",
            text="<br/>_ Correct<br/>- Wrong",
            points=1.0,
            answers=[
                Answer(text="Correct", is_correct=True),
                Answer(text="Wrong", is_correct=False),
            ],
            line_number=1,
            question_id="q_1",
        )

        presentation, feedback, resprocessing = create_question(question)

        assert 'response_lid ident="MCSR"' in presentation
        assert 'rcardinality="Single"' in presentation
        assert "response_0" in feedback

    def test_creates_multiple_choice_question_xml(self) -> None:
        """Multiple choice questions should generate correct XML structure."""
        question = Question(
            question_type=QUESTION_TYPE_MC_MULTI,
            title="Test MC Multi",
            text="<br/>_ Correct<br/>- Wrong<br/>_ Also Correct",
            points=2.0,
            answers=[
                Answer(text="Correct", is_correct=True),
                Answer(text="Wrong", is_correct=False),
                Answer(text="Also Correct", is_correct=True),
            ],
            line_number=1,
            question_id="q_1",
        )

        presentation, feedback, resprocessing = create_question(question)

        assert 'response_lid ident="MCMR"' in presentation
        assert 'rcardinality="Multiple"' in presentation


class TestConvertToQti:
    """Tests for convert_to_qti function."""

    def test_converts_questions_to_xml(self) -> None:
        """Should generate valid QTI XML document."""
        questions = [
            Question(
                question_type=QUESTION_TYPE_MC_SINGLE,
                title="Q1",
                text="<br/>_ A<br/>- B",
                points=1.0,
                answers=[
                    Answer(text="A", is_correct=True),
                    Answer(text="B", is_correct=False),
                ],
                line_number=1,
                question_id="q_1",
            ),
        ]

        result = convert_to_qti(questions)

        assert '<?xml version="1.0" encoding="utf-8"?>' in result
        assert "<questestinterop>" in result
        assert "</questestinterop>" in result
        assert 'item ident="q_1"' in result
        assert 'title="Q1"' in result

    def test_handles_multiple_questions(self) -> None:
        """Should handle multiple questions correctly."""
        questions = [
            Question(
                question_type=QUESTION_TYPE_MC_SINGLE,
                title="Q1",
                text="<br/>_ A",
                points=1.0,
                answers=[Answer(text="A", is_correct=True)],
                line_number=1,
                question_id="q_1",
            ),
            Question(
                question_type=QUESTION_TYPE_GAP,
                title="Q2",
                text="[gap]answer[/gap]",
                points=1.0,
                line_number=5,
                question_id="q_5",
            ),
        ]

        result = convert_to_qti(questions)

        assert 'item ident="q_1"' in result
        assert 'item ident="q_5"' in result
        assert 'title="Q1"' in result
        assert 'title="Q2"' in result

    def test_decvar_has_empty_format(self) -> None:
        """decvar should be empty for ILIAS compatibility."""
        questions = [
            Question(
                question_type=QUESTION_TYPE_MC_SINGLE,
                title="Q1",
                text="<br/>_ A",
                points=2.0,
                answers=[Answer(text="A", is_correct=True)],
                line_number=1,
                question_id="q_1",
            ),
        ]

        result = convert_to_qti(questions)

        assert "<decvar>" in result
        assert "</decvar>" in result

    def test_correct_answer_has_question_points(self) -> None:
        """Correct answer should have question points in setvar."""
        questions = [
            Question(
                question_type=QUESTION_TYPE_MC_SINGLE,
                title="Q1",
                text="<br/>_ A<br/>- B",
                points=2.0,
                answers=[Answer(text="A", is_correct=True), Answer(text="B", is_correct=False)],
                line_number=1,
                question_id="q_1",
            ),
        ]

        result = convert_to_qti(questions)

        assert '<setvar action="Add">2.000000</setvar>' in result

    def test_escapes_quotes_in_title_attributes(self) -> None:
        """Quotes in question titles should be escaped in XML attributes."""
        questions = [
            Question(
                question_type=QUESTION_TYPE_MC_SINGLE,
                title='Sequence X="ACGU" is from alphabet {A,C,G,U}. What is |X|?',
                text="<br/>_ 4<br/>- 12",
                points=2.0,
                answers=[
                    Answer(text="4", is_correct=False),
                    Answer(text="12", is_correct=True),
                ],
                line_number=1,
                question_id="q_1",
            ),
        ]

        result = convert_to_qti(questions)

        assert (
            'title="Sequence X=&quot;ACGU&quot; is from alphabet {A,C,G,U}. What is |X|?"' in result
        )
        assert (
            'label="Sequence X=&quot;ACGU&quot; is from alphabet {A,C,G,U}. What is |X|?"' in result
        )
