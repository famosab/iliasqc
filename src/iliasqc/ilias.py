"""ILIAS archive creation for iliasqc."""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
import zipfile
from fractions import Fraction
from pathlib import Path


def create_manifest(
    qpl_id: str,
    title: str,
    description: str,
    question_ids: list[str] | None = None,
    timestamp: str | None = None,
) -> str:
    """Create the ILIAS question pool manifest XML.

    Parameters
    ----------
    qpl_id:
        The question pool ID.
    title:
        The pool title.
    description:
        The pool description.
    question_ids:
        List of QTI question IDs. If None, uses the pool ID as the question ID.
    timestamp:
        The export timestamp (e.g., "1712345678").

    Returns
    -------
    str
        The manifest XML as a string.
    """
    if question_ids is None:
        question_ids = [qpl_id]

    if timestamp is None:
        timestamp = qpl_id

    normalized_ids = []
    for qid in question_ids:
        if "_qst_" in qid:
            normalized_ids.append(qid.split("_qst_")[-1])
        else:
            normalized_ids.append(qid)

    # tiqi uses qpl_id for PCID and TriggerQuestion entries
    qref_entries = "".join(f'<Question QRef="il_1600_qst_{qid}"/>' for qid in normalized_ids)
    pcid = qpl_id  # Use pool ID, not question ID
    trigger_entries = f'<TriggerQuestion Id="{qpl_id}"></TriggerQuestion>'

    manifest = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<!DOCTYPE Test SYSTEM "http://www.ilias.uni-koeln.de/download/dtd/ilias_co.dtd">'
        f"<!--Export of ILIAS Test Questionpool {qpl_id} of installation 1600-->"
        '<ContentObject Type="Questionpool_Test">'
        "<MetaData>"
        '<General Structure="Hierarchical">'
        f'<Identifier Catalog="ILIAS" Entry="il_1600_qpl_{qpl_id}"/>'
        f'<Title Language="de">{title}</Title>'
        '<Language Language="de"/>'
        f'<Description Language="de">{description}</Description>'
        '<Keyword Language="en"></Keyword>'
        "</General>"
        "</MetaData>"
        "<Settings>"
        "<ShowTaxonomies>0</ShowTaxonomies>"
        "<SkillService>0</SkillService>"
        "</Settings>"
        "<PageObject>"
        f'<PageContent PCID="{pcid}">'
        f"{qref_entries}"
        "</PageContent>"
        "</PageObject>"
        "<QuestionSkillAssignments>"
        f"{trigger_entries}"
        "</QuestionSkillAssignments>"
        "</ContentObject>"
    )
    return manifest


def create_export_xml(
    qpl_id: str,
    qti_id: str,
    export_timestamp: str | None = None,
    nic: str = "0",
) -> str:
    """Create the ILIAS export.xml file.

    Parameters
    ----------
    qpl_id:
        The question pool ID.
    qti_id:
        The QTI question ID.
    export_timestamp:
        Optional export timestamp (e.g., "1712345678").
    nic:
        The NIC (Network Installation Code), defaults to "0".

    Returns
    -------
    str
        The export XML as a string.
    """
    if export_timestamp is None:
        export_timestamp = qpl_id

    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<exp:Export InstallationId="1600" InstallationUrl="https://example.ilias.de" '
        'Entity="qpl" SchemaVersion="4.1.0" '
        'Type="qpl" '
        'xmlns:exp="http://www.ilias.de/Services/Export/exp/4_1" '
        'xmlns="http://www.ilias.de/Modules/TestQuestionPool/htlm/4_1">'
        f'<exp:ExportItem Id="{qpl_id}"></exp:ExportItem>'
        "</exp:Export>"
    )


def create_manifest_file(
    qpl_id: str,
    title: str,
    timestamp: str | None = None,
    nic: str = "0",
    has_media: bool = False,
) -> str:
    """Create the manifest.xml file for Native ILIAS Export.

    Parameters
    ----------
    qpl_id:
        The question pool ID.
    title:
        The pool title.
    timestamp:
        The export timestamp (e.g., "1712345678"). If None, uses qpl_id.
    nic:
        The Network Installation Code, defaults to "0".
    has_media:
        Whether media objects are included.

    Returns
    -------
    str
        The manifest.xml as a string.
    """
    if timestamp is None:
        timestamp = qpl_id

    qpl_xml_path = f"{timestamp}__{nic}__qpl_{qpl_id}.xml"
    qti_xml_path = f"{timestamp}__{nic}__qti_{qpl_id}.xml"
    export_xml_path = "Modules/TestQuestionPool/set_1/export.xml"
    services_export_xml_path = "Services/Export/set_1/export.xml"

    export_files = [
        f'<ExportFile Component="Modules/TestQuestionPool" Path="{qpl_xml_path}"/>',
        f'<ExportFile Component="Modules/TestQuestionPool" Path="{qti_xml_path}"/>',
        f'<ExportFile Component="Modules/TestQuestionPool" Path="{export_xml_path}"/>',
        f'<ExportFile Component="Services/Export" Path="{services_export_xml_path}"/>',
    ]

    if has_media:
        export_files.append('<ExportFile Component="Modules/TestQuestionPool" Path="objects/"/>')

    export_files_str = "\n  ".join(export_files)

    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        "<!--Generated by ILIAS XmlWriter-->"
        f'<Manifest MainEntity="qpl" Title="{title}" InstallationId="1600" '
        'InstallationUrl="https://example.ilias.de">'
        "<Information>"
        "<MainEntity>qpl</MainEntity>"
        "</Information>"
        f"{export_files_str}"
        "</Manifest>"
    )


def create_ilias_archive(
    qti_content: str,
    output_dir: str | Path,
    title: str,
    description: str,
    unique_id: str | None = None,
    question_ids: list[str] | None = None,
    folder_timestamp: str | None = None,
    nic: str = "1600",
) -> Path:
    """Create ILIAS-compatible archive structure following Native Export schema.

    Parameters
    ----------
    qti_content:
        The QTI XML content as a string.
    output_dir:
        Directory where the zip file will be created.
    title:
        The question pool title.
    description:
        The pool description.
    unique_id:
        Optional unique ID for the archive. If not provided,
        a deterministic ID is generated from the content.
    question_ids:
        List of question IDs for the manifest.
    folder_timestamp:
        Optional timestamp for the folder/zip name. If not provided,
        a deterministic timestamp is generated from the content.
    nic:
        The Network Installation Code, defaults to "1600".

    Returns
    -------
    Path
        Path to the created zip file.
    """
    if unique_id is None:
        unique_id = "0000000"

    qpl_id = unique_id

    if folder_timestamp is None:
        fingerprint = f"{unique_id}\n{title}\n{description}\n{qti_content}".encode()
        digest = hashlib.sha1(fingerprint).hexdigest()
        timestamp_int = int(digest[:12], 16) % 9000000000 + 1000000000
        folder_timestamp = str(timestamp_int)

    output_dir = Path(output_dir)
    folder_name = f"{folder_timestamp}__{nic}__qpl_{qpl_id}"
    temp_dir = output_dir / folder_name

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    (temp_dir / "objects").mkdir(exist_ok=True)

    qpl_xml_filename = temp_dir / f"{folder_timestamp}__{nic}__qpl_{qpl_id}.xml"
    qpl_manifest = create_manifest(qpl_id, title, description, None, folder_timestamp)
    qpl_xml_filename.write_text(qpl_manifest, encoding="utf-8")

    qti_xml_filename = temp_dir / f"{folder_timestamp}__{nic}__qti_{qpl_id}.xml"
    qti_xml_filename.write_text(qti_content, encoding="utf-8")

    export_dir = temp_dir / "Modules" / "TestQuestionPool" / "set_1"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_xml = '<?xml version="1.0" encoding="utf-8"?>\n'
    export_xml += "<!--Generated by ILIAS XmlWriter-->\n"
    export_xml += '<exp:Export InstallationId="1600" InstallationUrl="https://example.ilias.de" '
    export_xml += 'Entity="qpl" SchemaVersion="4.1.0" '
    export_xml += 'xmlns:exp="http://www.ilias.de/Services/Export/exp/4_1" '
    export_xml += 'xmlns="http://www.ilias.de/Modules/TestQuestionPool/htlm/4_1">'
    export_xml += f'<exp:ExportItem Id="{qpl_id}"></exp:ExportItem>'
    export_xml += "</exp:Export>\n"
    (export_dir / "export.xml").write_text(export_xml, encoding="utf-8")

    services_export_dir = temp_dir / "Services" / "Export" / "set_1"
    services_export_dir.mkdir(parents=True, exist_ok=True)
    services_export_xml = '<?xml version="1.0" encoding="utf-8"?>\n'
    services_export_xml += "<!--Generated by ILIAS XmlWriter-->\n"
    services_export_xml += (
        '<exp:Export InstallationId="1600" InstallationUrl="https://example.ilias.de" '
    )
    services_export_xml += 'Entity="qpl" SchemaVersion="4.1.0" '
    services_export_xml += 'xmlns:exp="http://www.ilias.de/Services/Export/exp/4_1" '
    services_export_xml += 'xmlns="http://www.ilias.de/Services/Export/exp/4_1">'
    services_export_xml += f'<exp:ExportItem Id="{qpl_id}"></exp:ExportItem>'
    services_export_xml += "</exp:Export>\n"
    (services_export_dir / "export.xml").write_text(services_export_xml, encoding="utf-8")

    manifest_xml = create_manifest_file(qpl_id, title, folder_timestamp, nic)
    (temp_dir / "manifest.xml").write_text(manifest_xml, encoding="utf-8")

    zip_filename = output_dir / f"{folder_name}.zip"
    with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir.parent)
                zf.write(file_path, arcname)

    shutil.rmtree(temp_dir)

    return zip_filename


def update_pool_overview_csv(
    output_dir: str | Path,
    overview_rows: list[dict],
    overview_filename: str = "pool_overview.csv",
) -> tuple[Path, list[dict]] | tuple[None, None]:
    """Update an overview CSV with pool information.

    Parameters
    ----------
    output_dir:
        Directory containing the overview CSV.
    overview_rows:
        List of dictionaries with keys: pool_zip_name, ilias_pool_name,
        question_count, points_per_question.
    overview_filename:
        Name of the overview CSV file.

    Returns
    -------
    tuple[Path, list[dict]] | tuple[None, None]
        Path to the updated CSV and list of merged rows, or (None, None)
        if no rows were provided.
    """
    if not overview_rows:
        return None, None

    output_dir = Path(output_dir)
    overview_path = output_dir / overview_filename
    fieldnames = [
        "pool_zip_name",
        "ilias_pool_name",
        "question_count",
        "points_per_question",
    ]

    merged_rows: dict[str, dict] = {}

    if overview_path.exists():
        with open(overview_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pool_zip_name = row.get("pool_zip_name", "").strip()
                if pool_zip_name:
                    merged_rows[pool_zip_name] = {
                        "pool_zip_name": pool_zip_name,
                        "ilias_pool_name": row.get("ilias_pool_name", ""),
                        "question_count": row.get("question_count", ""),
                        "points_per_question": row.get("points_per_question", ""),
                    }

    for row in overview_rows:
        pool_zip_name = str(row.get("pool_zip_name", "")).strip()
        if not pool_zip_name:
            continue
        merged_rows[pool_zip_name] = {
            "pool_zip_name": pool_zip_name,
            "ilias_pool_name": row.get("ilias_pool_name", ""),
            "question_count": row.get("question_count", ""),
            "points_per_question": row.get("points_per_question", ""),
        }

    with open(overview_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for pool_zip_name in sorted(merged_rows.keys()):
            writer.writerow(merged_rows[pool_zip_name])

    return overview_path, list(merged_rows.values())


def _format_point_label(points: Fraction) -> str:
    """Format point values for readable CSV headers/labels."""
    if points.denominator == 1:
        return str(points.numerator)
    return f"{points.numerator}_{points.denominator}"


def _build_combination_text(points_by_category: list[Fraction], counts_by_category: dict) -> str:
    """Create compact text like '2x3pt + 7x2pt'."""
    parts = []
    for points in sorted(points_by_category, reverse=True):
        count = counts_by_category.get(points, 0)
        if count > 0:
            parts.append(f"{count}x{_format_point_label(points)}pt")
    return " + ".join(parts) if parts else "0"


def export_target_point_combinations_csv(
    output_dir: str | Path,
    overview_rows: list[dict],
    target_points: float = 20,
    combinations_filename: str | None = None,
    max_combinations: int = 12,
) -> tuple[Path | None, int]:
    """Export a curated set of balanced combinations that sum to target_points.

    Parameters
    ----------
    output_dir:
        Directory to write the combinations CSV.
    overview_rows:
        List of dictionaries with question pool information.
    target_points:
        Target total points for quiz combinations.
    combinations_filename:
        Name of the output CSV file.
    max_combinations:
        Maximum number of combinations to export.

    Returns
    -------
    tuple[Path | None, int]
        Path to the created CSV and number of combinations, or (None, 0)
        if no valid combinations could be generated.
    """
    try:
        target = Fraction(str(target_points).strip())
    except (ValueError, ZeroDivisionError) as err:
        raise ValueError(f"Invalid targetPoints value: {target_points}") from err

    if target <= 0:
        raise ValueError("targetPoints must be > 0")

    if not overview_rows:
        return None, 0

    if combinations_filename is None:
        combinations_filename = f"pool_combinations_{_format_point_label(target)}_points.csv"

    categories: list[tuple[Fraction, int]] = []
    for row in overview_rows:
        try:
            points = Fraction(str(row.get("points_per_question", "")).strip())
            question_count = int(float(str(row.get("question_count", "")).strip()))
        except (ValueError, ZeroDivisionError):
            continue

        if points <= 0 or question_count <= 0:
            continue
        categories.append((points, question_count))

    if not categories:
        return None, 0

    max_count_by_points: dict[Fraction, int] = {}
    for points, question_count in categories:
        max_count_by_points[points] = max(max_count_by_points.get(points, 0), question_count)

    sorted_points = sorted(max_count_by_points.keys(), reverse=True)
    combinations: list[dict] = []

    def backtrack(idx: int, remaining: Fraction, selection: dict) -> None:
        if idx == len(sorted_points):
            if remaining == 0:
                combinations.append(selection.copy())
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
        counts = [
            selection.get(points, 0) for points in sorted_points if selection.get(points, 0) > 0
        ]
        if len(counts) <= 1:
            return 9999.0
        mean_count = sum(counts) / float(len(counts))
        return sum(abs(count - mean_count) for count in counts) / float(len(counts))

    scored = []
    for selection in combinations:
        used_category_count = sum(1 for points in sorted_points if selection.get(points, 0) > 0)
        total_questions = sum(selection.get(points, 0) for points in sorted_points)
        scored.append(
            {
                "selection": selection,
                "used_categories": used_category_count,
                "total_questions": total_questions,
                "balance_score": round(balance_score(selection), 3),
            }
        )

    scored.sort(
        key=lambda item: (
            -item["used_categories"],
            item["balance_score"],
            item["total_questions"],
            _build_combination_text(sorted_points, item["selection"]),
        )
    )

    curated = scored[:max_combinations]

    output_dir = Path(output_dir)
    combination_path = output_dir / combinations_filename
    dynamic_count_headers = [f"count_{_format_point_label(p)}pt" for p in sorted_points]
    fieldnames = [
        "rank",
        "target_points",
        "total_questions",
        "used_point_categories",
        "balance_score",
        "combination",
    ] + dynamic_count_headers

    with open(combination_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, item in enumerate(curated, start=1):
            selection = item["selection"]
            row = {
                "rank": idx,
                "target_points": float(target),
                "total_questions": item["total_questions"],
                "used_point_categories": item["used_categories"],
                "balance_score": item["balance_score"],
                "combination": _build_combination_text(sorted_points, selection),
            }
            for points in sorted_points:
                row[f"count_{_format_point_label(points)}pt"] = selection.get(points, 0)
            writer.writerow(row)

    return combination_path, len(curated)
