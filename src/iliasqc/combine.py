"""Quiz combination generator for iliasqc.

This module handles generating multiple question pools filtered by point values
and finding optimal combinations to reach target point totals.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path


@dataclass
class PoolInfo:
    """Information about a generated question pool."""

    pool_name: str
    zip_filename: str
    question_count: int
    points_per_question: float
    zip_path: Path | None = None


@dataclass
class PoolCombination:
    """A valid combination of pools that sum to a target."""

    pools: dict[str, int] = field(default_factory=dict)
    total_points: float = 0.0
    total_questions: int = 0
    balance_score: float = 0.0

    def get_summary(self) -> str:
        """Get a human-readable summary of the combination."""
        parts = []
        for pool_name, count in sorted(self.pools.items()):
            if count > 0:
                parts.append(f"{count}x {pool_name}")
        return " + ".join(parts) if parts else "None"


def generate_pools_by_points(
    input_path: str | Path,
    output_dir: str | Path | None = None,
) -> list[PoolInfo]:
    """Generate separate pool zip files for each point value.

    Parameters
    ----------
    input_path:
        Path to the input question text file.
    output_dir:
        Directory for output zip files. Defaults to the input file's directory.

    Returns
    -------
    list[PoolInfo]
        List of PoolInfo objects for each generated pool.
    """
    from iliasqc.convert import txt_to_zip
    from iliasqc.parser import extract_metadata, extract_point_values, parse_question_file

    input_path = Path(input_path)
    if output_dir is None:
        output_dir = input_path.parent
    output_dir = Path(output_dir)

    title, description = extract_metadata(input_path)
    point_values = extract_point_values(input_path)
    all_questions = parse_question_file(input_path)

    pools: list[PoolInfo] = []

    for points in point_values:
        filtered_questions = [q for q in all_questions if q.points == points]
        question_count = len(filtered_questions)

        if question_count == 0:
            continue

        pool_title = f"{title} ({int(points)} points)"
        pool_filename = f"{title}_{int(points)}pt_pool.zip"
        pool_path = output_dir / pool_filename

        txt_to_zip(
            input_path,
            pool_path,
            title=pool_title,
            description=description,
            filter_points=points,
        )

        pools.append(
            PoolInfo(
                pool_name=pool_title,
                zip_filename=pool_filename,
                question_count=question_count,
                points_per_question=points,
                zip_path=pool_path,
            )
        )

    return pools


def find_combinations(
    pools: list[PoolInfo],
    target_points: float,
    max_combinations: int = 20,
) -> list[PoolCombination]:
    """Find balanced combinations of pools that sum to target points.

    Parameters
    ----------
    pools:
        List of available pools.
    target_points:
        Target total points.
    max_combinations:
        Maximum number of combinations to return.

    Returns
    -------
    list[PoolCombination]
        List of valid combinations, sorted by balance score.
    """
    if not pools:
        return []

    target = Fraction(str(target_points))
    if target <= 0:
        raise ValueError("Target points must be greater than 0")

    max_count_by_points: dict[Fraction, int] = {}
    pool_by_points: dict[Fraction, PoolInfo] = {}
    for pool in pools:
        points = Fraction(str(pool.points_per_question))
        max_count_by_points[points] = max(
            max_count_by_points.get(points, 0), pool.question_count
        )
        pool_by_points[points] = pool

    if not max_count_by_points:
        return []

    sorted_points = sorted(max_count_by_points.keys(), reverse=True)
    all_combinations: list[dict] = []

    def backtrack(idx: int, remaining: Fraction, selection: dict) -> None:
        if idx == len(sorted_points):
            if remaining == 0:
                all_combinations.append(selection.copy())
            return

        points = sorted_points[idx]
        max_by_points = int(remaining / points)
        max_by_availability = max_count_by_points[points]
        max_use = min(max_by_points, max_by_availability)

        for count in range(max_use, -1, -1):
            selection[points] = count
            backtrack(idx + 1, remaining - points * count, selection)

    backtrack(0, target, {})

    def balance_score(selection: dict) -> float:
        counts = [selection.get(p, 0) for p in sorted_points if selection.get(p, 0) > 0]
        if len(counts) <= 1:
            return 9999.0
        mean_count = sum(counts) / float(len(counts))
        return sum(abs(c - mean_count) for c in counts) / float(len(counts))

    scored_combinations = []
    for selection in all_combinations:
        used_categories = sum(1 for p in sorted_points if selection.get(p, 0) > 0)
        total_questions = sum(selection.get(p, 0) for p in sorted_points)

        combo = PoolCombination(
            pools={pool_by_points[p].pool_name: selection[p] for p in sorted_points},
            total_points=target_points,
            total_questions=total_questions,
            balance_score=round(balance_score(selection), 3),
        )
        scored_combinations.append(combo)

    scored_combinations.sort(
        key=lambda c: (
            -len([v for v in c.pools.values() if v > 0]),
            c.balance_score,
            c.total_questions,
        )
    )

    return scored_combinations[:max_combinations]


def export_combinations_csv(
    output_dir: str | Path,
    combinations: list[PoolCombination],
    target_points: float,
    filename: str | None = None,
) -> Path:
    """Export combinations to a CSV file.

    Parameters
    ----------
    output_dir:
        Directory for the output CSV file.
    combinations:
        List of PoolCombination objects.
    target_points:
        Target points used for these combinations.
    filename:
        Output filename. Defaults to "quiz_combinations.csv".

    Returns
    -------
    Path
        Path to the created CSV file.
    """
    output_dir = Path(output_dir)
    if filename is None:
        filename = "quiz_combinations.csv"

    csv_path = output_dir / filename

    if not combinations:
        csv_path.write_text(
            f"# No valid combinations found for {target_points} points\n",
            encoding="utf-8",
        )
        return csv_path

    pool_names = sorted(set(name for combo in combinations for name in combo.pools))

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Pool Combination", "Total Questions", "Balance Score"] + pool_names)

        for rank, combo in enumerate(combinations, start=1):
            row = [
                rank,
                combo.get_summary(),
                combo.total_questions,
                combo.balance_score,
            ]
            for pool_name in pool_names:
                row.append(combo.pools.get(pool_name, 0))
            writer.writerow(row)

    return csv_path


def format_combinations_table(
    combinations: list[PoolCombination],
    pools: list[PoolInfo],
    target_points: float,
) -> str:
    """Format combinations as a human-readable text table.

    Parameters
    ----------
    combinations:
        List of PoolCombination objects.
    pools:
        List of PoolInfo objects for reference.
    target_points:
        Target points.

    Returns
    -------
    str
        Formatted table as a string.
    """
    if not combinations:
        return f"No valid combinations found for {target_points} points.\n"

    pool_names = sorted(set(name for combo in combinations for name in combo.pools))

    col_widths = {
        "Rank": 5,
        "Questions": 10,
        "Balance": 8,
        "Combination": 50,
    }

    header = (
        f"Quiz Combinations for {target_points} Points\n"
        f"{'=' * 70}\n\n"
        f"Available Pools:\n"
    )

    for pool in sorted(pools, key=lambda p: p.points_per_question, reverse=True):
        header += f"  - {pool.pool_name}: {pool.question_count} questions\n"

    header += f"\n{'─' * 70}\n"
    header += f"{'Rank':<{col_widths['Rank']}} {'Questions':<{col_widths['Questions']}} {'Balance':<{col_widths['Balance']}} Combination\n"
    header += f"{'─' * 70}\n"

    lines = [header]

    for rank, combo in enumerate(combinations, start=1):
        balance_indicator = "●●○○" if combo.balance_score > 0.5 else "●●●○" if combo.balance_score > 0.2 else "●●●●"
        summary = combo.get_summary()
        if len(summary) > col_widths["Combination"]:
            summary = summary[: col_widths["Combination"] - 3] + "..."

        lines.append(
            f"{rank:<{col_widths['Rank']}} {combo.total_questions:<{col_widths['Questions']}} "
            f"{balance_indicator:<{col_widths['Balance']}} {summary}"
        )

    lines.append(f"{'─' * 70}\n")
    lines.append("Tip: Lower balance score = more diverse quiz\n")

    return "\n".join(lines)


def generate_quiz_combinations(
    input_path: str | Path,
    target_points: float,
    output_dir: str | Path | None = None,
) -> tuple[list[PoolInfo], list[PoolCombination]]:
    """Generate pools and find quiz combinations.

    This is the main entry point for the quiz combination feature.

    Parameters
    ----------
    input_path:
        Path to the input question text file.
    target_points:
        Target total points for quiz combinations.
    output_dir:
        Directory for output files. Defaults to the input file's directory.

    Returns
    -------
    tuple[list[PoolInfo], list[PoolCombination]]
        Tuple of (generated pools, valid combinations).

    Raises
    ------
    ValueError
        If no valid combinations can be found.
    """
    input_path = Path(input_path)
    if output_dir is None:
        output_dir = input_path.parent
    output_dir = Path(output_dir)

    pools = generate_pools_by_points(input_path, output_dir)

    if not pools:
        raise ValueError("No pools could be generated from the input file.")

    combinations = find_combinations(pools, target_points)

    if not combinations:
        raise ValueError(
            f"No valid combinations found for {target_points} points. "
            f"Available point values: {[p.points_per_question for p in pools]}"
        )

    return pools, combinations
