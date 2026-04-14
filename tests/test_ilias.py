"""Tests for iliasqc.ilias."""

import zipfile
from pathlib import Path

import pytest

from iliasqc.ilias import (
    create_ilias_archive,
    create_manifest,
    export_target_point_combinations_csv,
    update_pool_overview_csv,
)


class TestCreateManifest:
    """Tests for create_manifest function."""

    def test_creates_valid_manifest(self) -> None:
        """Manifest should contain all required elements."""
        manifest = create_manifest("12345", "Test Pool", "A test", "12345")

        assert '<?xml version="1.0" encoding="utf-8"?>' in manifest
        assert "Questionpool_Test" in manifest
        assert "Test Pool" in manifest
        assert "A test" in manifest
        assert "il_1600_qpl_12345" in manifest

    def test_manifest_has_qpl_and_qti_entries(self) -> None:
        """Manifest should reference root-level XML files."""
        from iliasqc.ilias import create_manifest_file

        manifest = create_manifest_file("12345", "Test", "1234567890", "0")
        assert "1234567890__0__qpl_12345.xml" in manifest
        assert "1234567890__0__qti_12345.xml" in manifest


class TestCreateIliasArchive:
    """Tests for create_ilias_archive function."""

    def test_creates_zip_file(self, tmp_path: Path) -> None:
        """Should create a valid zip archive."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item/></questestinterop>
        """

        result = create_ilias_archive(
            qti_content,
            tmp_path,
            "Test Pool",
            "Test Description",
            unique_id="1234567",
        )

        assert result.exists()
        assert result.suffix == ".zip"

    def test_zip_contains_required_files(self, tmp_path: Path) -> None:
        """Zip should contain manifest and QTI files."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item/></questestinterop>
        """

        result = create_ilias_archive(
            qti_content,
            tmp_path,
            "Test Pool",
            "Test Description",
            unique_id="1234567",
        )

        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
            assert any("qpl_" in name and name.endswith(".xml") for name in names)
            assert any("qti_" in name and name.endswith(".xml") for name in names)

    def test_zip_has_ilias_export_structure(self, tmp_path: Path) -> None:
        """Zip should have proper ILIAS export structure for import (tiqi style - no objects dir)."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item ident="test" title="Test"/></questestinterop>
        """

        result = create_ilias_archive(
            qti_content,
            tmp_path,
            "Test Pool",
            "Test Description",
            unique_id="1234567",
        )

        with zipfile.ZipFile(result) as zf:
            names = set(zf.namelist())
            folder_prefix = "1234567"
            has_qpl_xml = any(f"qpl_{folder_prefix}.xml" in n for n in names)
            has_qti_xml = any(f"qti_{folder_prefix}.xml" in n for n in names)
            has_folder_root = any(n.count("/") == 1 and f"qpl_{folder_prefix}" in n for n in names)
            assert has_qpl_xml, f"Missing qpl XML in {names}"
            assert has_qti_xml, f"Missing qti XML in {names}"
            assert has_folder_root, f"Missing folder root in {names}"

    def test_zip_xml_files_in_root_folder(self, tmp_path: Path) -> None:
        """QTI and QPL XML files should be in root folder, not in subdirectories."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item ident="test" title="Test"/></questestinterop>
        """

        result = create_ilias_archive(
            qti_content,
            tmp_path,
            "Test Pool",
            "Test Description",
            unique_id="1234567",
        )

        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
            root_xmls = [n for n in names if n.endswith(".xml") and n.count("/") == 1]
            assert any("qpl_" in n for n in root_xmls), f"QPL XML should be in root: {root_xmls}"
            assert any("qti_" in n for n in root_xmls), f"QTI XML should be in root: {root_xmls}"

    def test_manifest_has_information_element(self, tmp_path: Path) -> None:
        """manifest.xml should have Information element with MainEntity."""
        from iliasqc.ilias import create_manifest_file

        manifest = create_manifest_file("12345", "Test Pool", "1234567890", "0")
        assert "<Information>" in manifest
        assert "<MainEntity>qpl</MainEntity>" in manifest

    def test_export_xml_has_correct_namespace(self) -> None:
        """export.xml should use htm namespace."""
        from iliasqc.ilias import create_export_xml

        export = create_export_xml("12345", "54321")
        assert "http://www.ilias.de/Modules/TestQuestionPool/htlm/4_1" in export

    def test_qpl_has_pcid_attribute(self) -> None:
        """QPL should have PCID attribute in PageContent matching qpl_id (tiqi style)."""
        from iliasqc.ilias import create_manifest

        manifest = create_manifest("12345", "Test", "Desc", ["il_1600_qst_4"], "123")
        assert 'PageContent PCID="12345"' in manifest

    def test_trigger_question_uses_qpl_id(self) -> None:
        """TriggerQuestion Id should use qpl_id (tiqi style)."""
        from iliasqc.ilias import create_manifest

        manifest = create_manifest("12345", "Test", "Desc", ["il_1600_qst_4"], "123")
        assert '<TriggerQuestion Id="12345"></TriggerQuestion>' in manifest

    def test_keyword_uses_language_en(self) -> None:
        """Keyword should use Language='en'."""
        from iliasqc.ilias import create_manifest

        manifest = create_manifest("12345", "Test", "Desc", ["il_1600_qst_4"], "123")
        assert '<Keyword Language="en"></Keyword>' in manifest


class TestUpdatePoolOverviewCsv:
    """Tests for update_pool_overview_csv function."""

    def test_creates_csv_file(self, tmp_path: Path) -> None:
        """Should create overview CSV with correct columns."""
        rows = [
            {
                "pool_zip_name": "pool1.zip",
                "ilias_pool_name": "Pool 1",
                "question_count": "5",
                "points_per_question": "1",
            }
        ]

        path, merged = update_pool_overview_csv(tmp_path, rows)

        assert path is not None
        assert path.exists()

        content = path.read_text()
        assert "pool_zip_name" in content
        assert "ilias_pool_name" in content
        assert "question_count" in content
        assert "points_per_question" in content

    def test_merges_existing_rows(self, tmp_path: Path) -> None:
        """Should merge with existing CSV entries."""
        existing = [
            {
                "pool_zip_name": "existing.zip",
                "ilias_pool_name": "Existing",
                "question_count": "3",
                "points_per_question": "2",
            }
        ]
        update_pool_overview_csv(tmp_path, existing)

        new_rows = [
            {
                "pool_zip_name": "new.zip",
                "ilias_pool_name": "New",
                "question_count": "7",
                "points_per_question": "1",
            }
        ]
        path, merged = update_pool_overview_csv(tmp_path, new_rows)

        assert len(merged) == 2

    def test_returns_none_for_empty_rows(self, tmp_path: Path) -> None:
        """Should return (None, None) for empty input."""
        path, merged = update_pool_overview_csv(tmp_path, [])
        assert path is None
        assert merged is None


class TestExportTargetPointCombinationsCsv:
    """Tests for export_target_point_combinations_csv function."""

    def test_creates_combinations_csv(self, tmp_path: Path) -> None:
        """Should create combinations CSV."""
        overview_rows = [
            {
                "pool_zip_name": "pool1.zip",
                "ilias_pool_name": "Pool 1",
                "question_count": "5",
                "points_per_question": "1",
            },
            {
                "pool_zip_name": "pool2.zip",
                "ilias_pool_name": "Pool 2",
                "question_count": "10",
                "points_per_question": "2",
            },
        ]

        path, count = export_target_point_combinations_csv(tmp_path, overview_rows, target_points=4)

        assert path is not None
        assert path.exists()
        assert count >= 0

    def test_returns_none_for_empty_rows(self, tmp_path: Path) -> None:
        """Should return (None, 0) for empty input."""
        path, count = export_target_point_combinations_csv(tmp_path, [])
        assert path is None
        assert count == 0

    def test_raises_for_invalid_target_points(self, tmp_path: Path) -> None:
        """Should raise ValueError for invalid target points."""
        with pytest.raises(ValueError):
            export_target_point_combinations_csv(tmp_path, [], target_points=-1)
