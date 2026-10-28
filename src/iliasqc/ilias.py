"""ILIAS archive creation for iliasqc."""

from __future__ import annotations

import hashlib
import os
import shutil
import zipfile
from pathlib import Path


def _escape_xml(text: str) -> str:
    """Escape special XML characters in element content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _escape_xml_attr(text: str) -> str:
    """Escape special XML characters in attribute values."""
    return _escape_xml(text)


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

    # Use the exact question IDs from the parser (they must match QTI item idents)
    qref_entries = "".join(f'<Question QRef="{qid}"/>' for qid in question_ids)
    pcid = qpl_id  # Use pool ID, not question ID
    trigger_entries = f'<TriggerQuestion Id="{qpl_id}"></TriggerQuestion>'

    escaped_title = _escape_xml(title)
    escaped_description = _escape_xml(description)

    manifest = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<!DOCTYPE Test SYSTEM "http://www.ilias.uni-koeln.de/download/dtd/ilias_co.dtd">'
        f"<!--Export of ILIAS Test Questionpool {qpl_id} of installation 1600-->"
        '<ContentObject Type="Questionpool_Test">'
        "<MetaData>"
        '<General Structure="Hierarchical">'
        f'<Identifier Catalog="ILIAS" Entry="il_1600_qpl_{qpl_id}"/>'
        f'<Title Language="de">{escaped_title}</Title>'
        '<Language Language="de"/>'
        f'<Description Language="de">{escaped_description}</Description>'
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
    qpl_manifest = create_manifest(qpl_id, title, description, question_ids, folder_timestamp)
    qpl_xml_filename.write_text(qpl_manifest, encoding="utf-8")

    qti_xml_filename = temp_dir / f"{folder_timestamp}__{nic}__qti_{qpl_id}.xml"
    qti_xml_filename.write_text(qti_content, encoding="utf-8")

    zip_filename = output_dir / f"{folder_name}.zip"
    with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir.parent)
                zf.write(file_path, arcname)

    shutil.rmtree(temp_dir)

    return zip_filename
