"""Tests for iliasqc.ilias."""

import zipfile
from pathlib import Path

from iliasqc.ilias import (
    create_ilias_archive,
    create_manifest,
)


class TestCreateManifest:
    """Tests for create_manifest function."""

    def test_creates_valid_manifest(self) -> None:
        """Manifest should contain all required elements."""
        manifest = create_manifest("12345", "Test Pool", "A test", None, "12345")

        assert '<?xml version="1.0" encoding="utf-8"?>' in manifest
        assert "Questionpool_Test" in manifest
        assert "Test Pool" in manifest
        assert "A test" in manifest
        assert "il_1600_qpl_12345" in manifest


class TestTiqiParity:
    """Tests to ensure iliasqc output matches tiqi.py output format."""

    def test_manifest_uses_ilias_co_dtd(self, tmp_path: Path) -> None:
        """Manifest should use ILIAS CO DTD format (tiqi style)."""
        manifest = create_manifest("6599701", "Test Pool", "Description", None, "1234567890")

        assert (
            '<!DOCTYPE Test SYSTEM "http://www.ilias.uni-koeln.de/download/dtd/ilias_co.dtd">'
            in manifest
        )
        assert "il_1600_qpl_6599701" in manifest
        assert '<Title Language="de">Test Pool</Title>' in manifest
        assert '<Description Language="de">Description</Description>' in manifest

    def test_manifest_pcid_uses_qpl_id(self, tmp_path: Path) -> None:
        """PCID should use qpl_id, not question ID (tiqi style)."""
        manifest = create_manifest("6599701", "Test Pool", "Description", None, "1234567890")

        assert 'PCID="6599701"' in manifest

    def test_manifest_trigger_uses_qpl_id(self, tmp_path: Path) -> None:
        """TriggerQuestion Id should use qpl_id (tiqi style)."""
        manifest = create_manifest("6599701", "Test Pool", "Description", None, "1234567890")

        assert '<TriggerQuestion Id="6599701"></TriggerQuestion>' in manifest

    def test_archive_uses_nic_1600(self, tmp_path: Path) -> None:
        """Archive should use NIC 1600 (tiqi style)."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item ident="test" title="Test"/></questestinterop>
        """

        result = create_ilias_archive(
            qti_content,
            tmp_path,
            "Test Pool",
            "Test Description",
            unique_id="6599701",
            folder_timestamp="1234567890",
        )

        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
            assert any("1234567890__1600__qpl_6599701" in n for n in names)

    def test_qpl_file_contains_manifest_not_qti(self, tmp_path: Path) -> None:
        """QPL file should contain manifest XML, not QTI content."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item ident="test" title="Test"/></questestinterop>
        """

        result = create_ilias_archive(
            qti_content,
            tmp_path,
            "Test Pool",
            "Test Description",
            unique_id="6599701",
            folder_timestamp="1234567890",
        )

        with zipfile.ZipFile(result) as zf:
            qpl_file = [
                n for n in zf.namelist() if "qpl_" in n and "qti_" not in n and n.endswith(".xml")
            ][0]
            qpl_content = zf.read(qpl_file).decode("utf-8")

            assert "Questionpool_Test" in qpl_content
            assert "il_1600_qpl_6599701" in qpl_content
            assert "questestinterop" not in qpl_content.lower()

    def test_qti_file_contains_qti_content(self, tmp_path: Path) -> None:
        """QTI file should contain question content, not manifest."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item ident="test" title="Test"/></questestinterop>
        """

        result = create_ilias_archive(
            qti_content,
            tmp_path,
            "Test Pool",
            "Test Description",
            unique_id="6599701",
            folder_timestamp="1234567890",
        )

        with zipfile.ZipFile(result) as zf:
            qti_file = [n for n in zf.namelist() if "qti_" in n][0]
            qti_file_content = zf.read(qti_file).decode("utf-8")

            assert "questestinterop" in qti_file_content
            assert "Questionpool_Test" not in qti_file_content


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
