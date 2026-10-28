"""Tests for iliasqc.quiz."""

import pytest
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
        assert "il_1600_tst_12345" in manifest
        # Should have PageObject wrappers (not Settings/TestType)
        assert "<PageObject>" in manifest
        assert "<PageContent>" in manifest
        # Should have Lifecycle section
        assert "<Lifecycle" in manifest
        assert "iliasqc" in manifest
        # Should have QuestionSkillAssignments with TriggerQuestion
        assert "<QuestionSkillAssignments>" in manifest
        assert "<TriggerQuestion" in manifest
        assert "<SkillsLevelThresholds>" in manifest

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
        # Should include xsi:schemaLocation (matching ILIAS export format)
        assert 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' in export_xml
        assert 'xsi:schemaLocation=' in export_xml


class TestCreateTestManifestFile:
    """Tests for create_test_manifest_file function."""

    def test_creates_valid_manifest(self) -> None:
        """Manifest file should have valid structure."""
        manifest = create_test_manifest_file("tst123", "Test Quiz")

        assert '<?xml version="1.0" encoding="utf-8"?>' in manifest
        assert "Manifest" in manifest
        assert 'MainEntity="tst"' in manifest
        assert "Test Quiz" in manifest
        # Should NOT include QTI file in export files (embedded quiz)
        assert "qti_" not in manifest
        # Should include all required export components
        assert 'Component="Services/MediaObjects"' in manifest
        assert 'Component="Modules/File"' in manifest
        assert 'Component="Modules/Test"' in manifest
        assert 'Component="Services/Object"' in manifest


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

    def test_zip_has_required_export_components(self, tmp_path: Path) -> None:
        """Zip should include all required export components."""
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
            assert any("Services/MediaObjects/set_1/export.xml" in n for n in names)
            assert any("Modules/File/set_1/export.xml" in n for n in names)
            assert any("Services/Object/set_1/export.xml" in n for n in names)

    def test_test_manifest_has_reference_structure(self, tmp_path: Path) -> None:
        """Test manifest XML should match ILIAS export format (reference zip)."""
        qti_content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE questestinterop SYSTEM "ims_qtiasiv1p2p1.dtd">
<!--Generated by ILIAS XmlWriter-->
<questestinterop>
<item ident="il_1600_qst_100" title="Test Question" maxattempts="1">
</item>
</questestinterop>
"""

        result = create_integrated_quiz_archive(
            qti_content,
            tmp_path,
            "Test Quiz",
            "Test Description",
            unique_id="6626203",
        )

        with zipfile.ZipFile(result) as zf:
            # Read the test manifest XML
            for name in zf.namelist():
                if "tst_" in name and name.endswith(".xml") and "/manifest.xml" not in name:
                    content = zf.read(name).decode()
                    # Should have PageObject wrappers with Question QRef
                    assert "<PageObject>" in content
                    assert "<PageContent>" in content
                    assert "<Question QRef=" in content
                    # Should have Lifecycle section
                    assert "<Lifecycle" in content
                    assert "Status=\"Draft\"" in content
                    # Should have TriggerQuestion
                    assert "<QuestionSkillAssignments>" in content
                    assert "<TriggerQuestion" in content
                    assert "<SkillsLevelThresholds>" in content
                    # Should NOT have Settings/TestType
                    assert "TestType" not in content
                    break
            else:
                pytest.fail("No test manifest XML found in zip")

    def test_object_export_has_dataset_structure(self, tmp_path: Path) -> None:
        """Object export.xml should include ds:DataSet and ds:Rec structure."""
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
            for name in zf.namelist():
                if "Services/Object" in name and "export.xml" in name:
                    content = zf.read(name).decode()
                    assert 'xmlns:ds="http://www.ilias.de/Services/DataSet/ds/4_3"' in content
                    assert "<ds:DataSet" in content
                    assert "<ds:Rec" in content
                    assert "<Common>" in content
                    assert "<ObjId>" in content
                    assert "xmlns:xsi" in content
                    assert "xsi:schemaLocation" in content
                    break
            else:
                pytest.fail("No object export.xml found in zip")

    def test_mediaobjects_export_has_reference_structure(self, tmp_path: Path) -> None:
        """MediaObjects export.xml should match ILIAS export format with schemaLocation."""
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
            for name in zf.namelist():
                if "Services/MediaObjects" in name and "export.xml" in name:
                    content = zf.read(name).decode()
                    assert 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' in content
                    assert "xsi:schemaLocation" in content
                    assert 'xmlns:ds="http://www.ilias.de/Services/DataSet/ds/4_3"' in content
                    # Should NOT have ExportItem (empty export)
                    assert "<exp:ExportItem" not in content
                    break
            else:
                pytest.fail("No MediaObjects export.xml found in zip")

    def test_file_export_has_reference_structure(self, tmp_path: Path) -> None:
        """File export.xml should match ILIAS export format with schemaLocation."""
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
            for name in zf.namelist():
                if "Modules/File" in name and "export.xml" in name:
                    content = zf.read(name).decode()
                    assert 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' in content
                    assert "xsi:schemaLocation" in content
                    # Should NOT have ExportItem (empty export)
                    assert "<exp:ExportItem" not in content
                    break
            else:
                pytest.fail("No File export.xml found in zip")

    def test_quiz_xml_structure_matches_reference(self, tmp_path: Path) -> None:
        """Overall zip structure should match the reference zip layout."""
        qti_content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE questestinterop SYSTEM "ims_qtiasiv1p2p1.dtd">
<!--Generated by ILIAS XmlWriter-->
<questestinterop>
<item ident="il_1600_qst_100" title="Test" maxattempts="1">
</item>
</questestinterop>
"""

        result = create_integrated_quiz_archive(
            qti_content,
            tmp_path,
            "Test Quiz",
            "Test Description",
            unique_id="6626203",
        )

        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
            # Should have these directories
            assert any("Modules/Test/set_1/" in n for n in names)
            assert any("Modules/File/set_1/" in n for n in names)
            assert any("Services/MediaObjects/set_1/" in n for n in names)
            assert any("Services/Object/set_1/" in n for n in names)
            assert any("objects/" in n for n in names)
            # Should NOT have QTI file as a separate export
            assert not any("QTI" in n or "qti.xml" in n for n in names)

    def test_qti_wrapped_in_assessment(self, tmp_path: Path) -> None:
        """QTI should be wrapped in assessment and section elements."""
        qti_content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE questestinterop SYSTEM "ims_qtiasiv1p2p1.dtd">
<!--Generated by ILIAS XmlWriter-->
<questestinterop>
<item ident="il_1600_qst_123" title="Test Question" maxattempts="1">
</item>
</questestinterop>
"""

        result = create_integrated_quiz_archive(
            qti_content,
            tmp_path,
            "Test Quiz",
            "Test Description",
            unique_id="1234567",
        )

        with zipfile.ZipFile(result) as zf:
            for name in zf.namelist():
                if "qti_" in name:
                    content = zf.read(name).decode()
                    assert "<assessment" in content
                    assert "</assessment>" in content
                    assert "<section" in content
                    assert "</section>" in content
                    assert "il_1600_tst_" in content
