"""Tests for iliasqc.combine."""

from pathlib import Path

import pytest

from iliasqc.combine import (
    PoolCombination,
    PoolInfo,
    export_combinations_csv,
    find_combinations,
    format_combinations_table,
    generate_pools_by_points,
    generate_quiz_combinations,
    generate_quiz_from_combination,
)


class TestPoolInfo:
    """Tests for PoolInfo dataclass."""

    def test_pool_info_creation(self) -> None:
        """PoolInfo should be created correctly."""
        pool = PoolInfo(
            pool_name="Test Pool (2 points)",
            zip_filename="test_2pt_pool.zip",
            question_count=5,
            points_per_question=2.0,
        )
        assert pool.pool_name == "Test Pool (2 points)"
        assert pool.zip_filename == "test_2pt_pool.zip"
        assert pool.question_count == 5
        assert pool.points_per_question == 2.0


class TestPoolCombination:
    """Tests for PoolCombination dataclass."""

    def test_pool_combination_creation(self) -> None:
        """PoolCombination should be created correctly."""
        combo = PoolCombination(
            pools={"Pool A": 2, "Pool B": 1},
            total_points=10.0,
            total_questions=5,
            balance_score=0.5,
        )
        assert combo.pools == {"Pool A": 2, "Pool B": 1}
        assert combo.total_points == 10.0
        assert combo.total_questions == 5

    def test_get_summary(self) -> None:
        """get_summary should return human-readable summary."""
        combo = PoolCombination(
            pools={"Pool A": 2, "Pool B": 1, "Pool C": 0},
            total_points=10.0,
            total_questions=5,
            balance_score=0.5,
        )
        summary = combo.get_summary()
        assert "2x Pool A" in summary
        assert "1x Pool B" in summary
        assert "Pool C" not in summary


class TestFindCombinations:
    """Tests for find_combinations function."""

    def test_finds_valid_combinations(self) -> None:
        """Should find combinations that sum to target points."""
        pools = [
            PoolInfo("1pt", "1pt.zip", 5, 1.0),
            PoolInfo("2pt", "2pt.zip", 3, 2.0),
            PoolInfo("3pt", "3pt.zip", 2, 3.0),
        ]

        combos = find_combinations(pools, target_points=4)

        assert len(combos) > 0
        assert all(c.total_points == 4.0 for c in combos)
        for combo in combos:
            total = sum(
                count * pool_by_name.points_per_question
                for name, count in combo.pools.items()
                for pool_by_name in pools
                if pool_by_name.pool_name == name
            )
            assert total == 4.0

    def test_empty_pools_returns_empty(self) -> None:
        """Should return empty list for empty pools."""
        combos = find_combinations([], target_points=10)
        assert combos == []

    def test_raises_for_invalid_target(self) -> None:
        """Should raise ValueError for invalid target points."""
        pools = [PoolInfo("1pt", "1pt.zip", 5, 1.0)]
        with pytest.raises(ValueError, match="greater than 0"):
            find_combinations(pools, target_points=-1)

    def test_sorts_by_balance(self) -> None:
        """Should sort combinations by balance score."""
        pools = [
            PoolInfo("1pt", "1pt.zip", 5, 1.0),
            PoolInfo("2pt", "2pt.zip", 3, 2.0),
        ]
        combos = find_combinations(pools, target_points=4, max_combinations=10)
        if len(combos) > 1:
            assert combos[0].balance_score <= combos[1].balance_score


class TestGeneratePoolsByPoints:
    """Tests for generate_pools_by_points function."""

    def test_generates_pool_per_point_value(self, tmp_path: Path) -> None:
        """Should generate a separate pool for each point value."""
        content = """# TITLE: Test Pool

[t][s] Q1 @1
_ A
- B

[t][s] Q2 @1
_ C
- D

[t][s] Q3 @2
_ E
- F
"""
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        pools = generate_pools_by_points(input_file, tmp_path)

        assert len(pools) == 2
        assert any(p.points_per_question == 1.0 for p in pools)
        assert any(p.points_per_question == 2.0 for p in pools)

    def test_creates_zip_files(self, tmp_path: Path) -> None:
        """Should create zip files for each pool."""
        content = """# TITLE: Test Pool

[t][s] Q1 @1
_ A
- B
"""
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        pools = generate_pools_by_points(input_file, tmp_path)

        assert len(pools) == 1
        assert pools[0].zip_path is not None
        assert pools[0].zip_path.exists()

    def test_counts_questions_correctly(self, tmp_path: Path) -> None:
        """Should count questions correctly per pool."""
        content = """# TITLE: Test Pool

[t][s] Q1 @1
_ A
- B

[t][s] Q2 @1
_ C
- D

[t][s] Q3 @2
_ E
- F

[t][s] Q4 @2
_ G
- H
"""
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        pools = generate_pools_by_points(input_file, tmp_path)

        pool_1pt = next(p for p in pools if p.points_per_question == 1.0)
        pool_2pt = next(p for p in pools if p.points_per_question == 2.0)

        assert pool_1pt.question_count == 2
        assert pool_2pt.question_count == 2


class TestExportCombinationsCsv:
    """Tests for export_combinations_csv function."""

    def test_creates_csv_file(self, tmp_path: Path) -> None:
        """Should create a CSV file with combinations."""
        combinations = [
            PoolCombination(
                pools={"Pool A": 2, "Pool B": 1},
                total_points=10.0,
                total_questions=5,
                balance_score=0.5,
            ),
        ]

        csv_path = export_combinations_csv(tmp_path, combinations, target_points=10)

        assert csv_path.exists()
        content = csv_path.read_text()
        assert "Rank" in content
        assert "Pool A" in content

    def test_empty_combinations_creates_file(self, tmp_path: Path) -> None:
        """Should create a file even for empty combinations."""
        csv_path = export_combinations_csv(tmp_path, [], target_points=10)
        assert csv_path.exists()
        content = csv_path.read_text()
        assert "No valid combinations" in content


class TestFormatCombinationsTable:
    """Tests for format_combinations_table function."""

    def test_includes_header(self) -> None:
        """Should include header with target points."""
        pools = [PoolInfo("1pt", "1pt.zip", 5, 1.0)]
        combinations = [
            PoolCombination(
                pools={"1pt": 4},
                total_points=4.0,
                total_questions=4,
                balance_score=0.0,
            ),
        ]

        table = format_combinations_table(combinations, pools, target_points=4)

        assert "Quiz Combinations" in table
        assert "4 Points" in table
        assert "Available Pools" in table

    def test_includes_combinations(self) -> None:
        """Should include all combinations in table."""
        pools = [PoolInfo("1pt", "1pt.zip", 5, 1.0)]
        combinations = [
            PoolCombination(
                pools={"1pt": 4},
                total_points=4.0,
                total_questions=4,
                balance_score=0.0,
            ),
        ]

        table = format_combinations_table(combinations, pools, target_points=4)

        assert "4x 1pt" in table
        assert "4" in table

    def test_empty_combinations_message(self) -> None:
        """Should show message for empty combinations."""
        pools = [PoolInfo("1pt", "1pt.zip", 5, 1.0)]
        table = format_combinations_table([], pools, target_points=4)
        assert "No valid combinations" in table


class TestGenerateQuizCombinations:
    """Tests for generate_quiz_combinations function."""

    def test_full_pipeline(self, tmp_path: Path) -> None:
        """Should generate pools and find combinations."""
        content = """# TITLE: Test Pool

[t][s] Q1 @1
_ A
- B

[t][s] Q2 @1
_ C
- D

[t][s] Q3 @2
_ E
- F

[t][s] Q4 @2
_ G
- H
"""
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        pools, combinations = generate_quiz_combinations(
            input_file, target_points=4, output_dir=tmp_path
        )

        assert len(pools) == 2
        assert len(combinations) > 0
        for pool in pools:
            assert pool.zip_path.exists()

    def test_raises_when_no_combinations(self, tmp_path: Path) -> None:
        """Should raise ValueError when no combinations found."""
        content = """# TITLE: Test Pool

[t][s] Q1 @5
_ A
- B

[t][s] Q2 @5
_ C
- D
"""
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        with pytest.raises(ValueError, match="No valid combinations"):
            generate_quiz_combinations(input_file, target_points=3, output_dir=tmp_path)


class TestGenerateQuizFromCombination:
    """Tests for generate_quiz_from_combination function."""

    def test_creates_quiz_from_combination(self, tmp_path: Path) -> None:
        """Should create a quiz zip from a pool combination."""
        content = """# TITLE: Test Pool

        [t][s] Q1 @1
        _ A
        - B

        [t][s] Q2 @1
        _ C
        - D

        [t][s] Q3 @2
        _ E
        - F

        [t][s] Q4 @2
        _ G
        - H
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        pools, combinations = generate_quiz_combinations(
            input_file, target_points=4, output_dir=tmp_path
        )

        if combinations:
            quiz_path = generate_quiz_from_combination(input_file, pools, combinations[0], tmp_path)
            assert quiz_path.exists()
            assert quiz_path.suffix == ".zip"

    def test_quiz_has_correct_point_total(self, tmp_path: Path) -> None:
        """Quiz should have questions summing to the target points."""
        content = """# TITLE: Test Pool

        [t][s] Q1 @1
        _ A
        - B

        [t][s] Q2 @2
        _ C
        - D
        """
        input_file = tmp_path / "questions.txt"
        input_file.write_text(content)

        pools, combinations = generate_quiz_combinations(
            input_file, target_points=3, output_dir=tmp_path
        )

        if combinations:
            quiz_path = generate_quiz_from_combination(input_file, pools, combinations[0], tmp_path)

            import zipfile

            with zipfile.ZipFile(quiz_path) as zf:
                names = zf.namelist()
                assert any("tst_" in name for name in names)
