"""Tests for iliasqc.quiz."""

import zipfile
from pathlib import Path

from iliasqc.quiz import (
    create_integrated_quiz_archive,
    create_quiz_archive,
    create_test_export_xml,
    create_test_manifest,
    create_test_manifest_file,
)


class TestCreateTestManifest:
    """Tests for create_test_manifest function."""

    def test_creates_valid_manifest(self) -> None:
        """Manifest should contain all required elements."""
        manifest = create_test_manifest("12345", "Test Quiz", "A test quiz", ["pool1", "pool2"])

        assert '<?xml version="1.0" encoding="utf-8"?>' in manifest
        assert "Test" in manifest
        assert "Test Quiz" in manifest
        assert "TestType" in manifest
        assert "il_1600_tst_12345" in manifest

    def test_includes_pool_references(self) -> None:
        """Manifest should include pool references."""
        manifest = create_test_manifest("12345", "Quiz", "Desc", ["pool1", "pool2"])

        assert "il_1600_qst_pool1" in manifest
        assert "il_1600_qst_pool2" in manifest


class TestCreateTestExportXml:
    """Tests for create_test_export_xml function."""

    def test_creates_valid_export_xml(self) -> None:
        """Export XML should have valid structure."""
        export_xml = create_test_export_xml("tst123", ["qti_1", "qti_2"])

        assert '<?xml version="1.0" encoding="utf-8"?>' in export_xml
        assert "exp:Export" in export_xml
        assert 'Entity="tst"' in export_xml
        assert 'Id="tst123"' in export_xml


class TestCreateTestManifestFile:
    """Tests for create_test_manifest_file function."""

    def test_creates_valid_manifest(self) -> None:
        """Manifest file should have valid structure."""
        manifest = create_test_manifest_file("tst123", "Test Quiz")

        assert '<?xml version="1.0" encoding="utf-8"?>' in manifest
        assert "Manifest" in manifest
        assert 'MainEntity="tst"' in manifest
        assert "Test Quiz" in manifest


class TestCreateQuizArchive:
    """Tests for create_quiz_archive function."""

    def test_creates_zip_file(self, tmp_path: Path) -> None:
        """Should create a valid zip archive."""
        pool_zip_1 = tmp_path / "pool1.zip"
        pool_zip_2 = tmp_path / "pool2.zip"

        pool_content = """<?xml version="1.0"?>
        <questestinterop><item ident="test" title="Test"/></questestinterop>
        """
        with zipfile.ZipFile(pool_zip_1, "w") as zf:
            zf.writestr("test.xml", pool_content)
        with zipfile.ZipFile(pool_zip_2, "w") as zf:
            zf.writestr("test.xml", pool_content)

        result = create_quiz_archive(
            [pool_zip_1, pool_zip_2],
            tmp_path,
            "Test Quiz",
            "Test Description",
            unique_id="1234567",
        )

        assert result.exists()
        assert result.suffix == ".zip"

    def test_zip_contains_required_files(self, tmp_path: Path) -> None:
        """Zip should contain manifest and test files."""
        pool_zip = tmp_path / "pool1.zip"
        pool_content = """<?xml version="1.0"?>
        <questestinterop><item/></questestinterop>
        """
        with zipfile.ZipFile(pool_zip, "w") as zf:
            zf.writestr("test.xml", pool_content)

        result = create_quiz_archive(
            [pool_zip],
            tmp_path,
            "Test Quiz",
            "Test",
            unique_id="1234567",
        )

        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
            assert any("export.xml" in n for n in names)
            assert any("tst_" in n and n.endswith(".xml") for n in names)


class TestCreateIntegratedQuizArchive:
    """Tests for create_integrated_quiz_archive function."""

    def test_creates_zip_file(self, tmp_path: Path) -> None:
        """Should create a valid zip archive."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item ident="test" title="Test"/></questestinterop>
        """

        result = create_integrated_quiz_archive(
            qti_content,
            tmp_path,
            "Test Quiz",
            "Test Description",
            unique_id="1234567",
        )

        assert result.exists()
        assert result.suffix == ".zip"

    def test_zip_has_valid_structure(self, tmp_path: Path) -> None:
        """Zip should have proper ILIAS export structure."""
        qti_content = """<?xml version="1.0"?>
        <questestinterop><item ident="test" title="Test"/></questestinterop>
        """

        result = create_integrated_quiz_archive(
            qti_content,
            tmp_path,
            "Test Quiz",
            "Test Description",
            unique_id="1234567",
        )

        with zipfile.ZipFile(result) as zf:
            names = set(zf.namelist())
            folder_prefix = "1234567"
            has_manifest = any(
                n.endswith("/manifest.xml") and folder_prefix[:7] in n for n in names
            )
            has_export = any("Modules/Test/set_1/export.xml" in n for n in names)
            has_test = any("tst_" in n and n.endswith(".xml") for n in names)
            has_qti = any("qti_" in n and n.endswith(".xml") for n in names)
            assert has_manifest, f"Missing manifest.xml in {names}"
            assert has_export, f"Missing export.xml in {names}"
            assert has_test, f"Missing tst xml in {names}"
            assert has_qti, f"Missing qti xml in {names}"
