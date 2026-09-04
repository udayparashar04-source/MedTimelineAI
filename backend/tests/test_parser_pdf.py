"""PDF fixture integration tests for the deterministic parser."""

from pathlib import Path

import pytest

from app.services.parser import parse_pdf, parse_pdf_bytes
from app.services.parser.text_extract import PdfTextExtractionError
from helpers_pdf import build_text_pdf


@pytest.fixture(scope="module", autouse=True)
def ensure_fixtures(fixtures_dir: Path):
    """Create fixtures if missing so tests are self-contained."""
    from generate_fixtures import main

    main()
    assert (fixtures_dir / "multi_test_report.pdf").is_file()


def test_successful_extraction_from_pdf(fixtures_dir: Path):
    report = parse_pdf(fixtures_dir / "multi_test_report.pdf")
    assert report.parser_version
    assert report.report_date == "2024-03-15"
    assert {"Hemoglobin", "WBC", "Glucose", "Creatinine", "HbA1c"} <= report.result_names()

    glucose = report.get_result("Glucose")
    assert glucose is not None
    assert glucose.value_numeric == 98.0
    assert glucose.unit.lower() == "mg/dl"
    assert glucose.source.page == 1


def test_date_detection_from_pdf(fixtures_dir: Path):
    report = parse_pdf(fixtures_dir / "date_only_sparse.pdf")
    assert report.report_date == "2025-09-03"
    assert report.results == []


def test_aliases_from_pdf(fixtures_dir: Path):
    report = parse_pdf(fixtures_dir / "alias_report.pdf")
    assert report.get_result("Hemoglobin") is not None
    assert report.get_result("Glucose") is not None
    assert report.get_result("ALT") is not None
    assert report.get_result("TSH") is not None
    assert report.get_result("Hgb") is None


def test_missing_tests_not_zero_from_pdf(fixtures_dir: Path):
    report = parse_pdf(fixtures_dir / "alias_report.pdf")
    assert report.get_result("Creatinine") is None
    assert report.get_result("Platelets") is None
    assert all(
        not (r.canonical_name == "Creatinine" and r.value_numeric == 0)
        for r in report.results
    )


def test_multiple_tests_in_one_report(fixtures_dir: Path):
    report = parse_pdf(fixtures_dir / "multi_test_report.pdf")
    assert len(report.results) >= 4
    units = {r.canonical_name: r.unit for r in report.results}
    assert units["Hemoglobin"]
    assert units["Creatinine"]


def test_empty_pdf_bytes_raise():
    with pytest.raises(PdfTextExtractionError):
        parse_pdf_bytes(b"")


def test_malformed_pdf_raises(fixtures_dir: Path):
    with pytest.raises(PdfTextExtractionError):
        parse_pdf(fixtures_dir / "malformed.pdf")


def test_empty_text_layer_pdf_has_no_results(fixtures_dir: Path):
    report = parse_pdf(fixtures_dir / "empty_text.pdf")
    assert report.results == []
    assert report.report_date is None


def test_parse_pdf_bytes_roundtrip():
    data = build_text_pdf(
        [
            "Collection Date: 20/08/2023",
            "Potassium 4.1 mEq/L",
            "Sodium 140 mEq/L",
        ]
    )
    report = parse_pdf_bytes(data)
    assert report.report_date == "2023-08-20"
    assert report.get_result("Potassium").value_numeric == 4.1
    assert report.get_result("Sodium").value_numeric == 140.0
    assert report.get_result("Glucose") is None


def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(PdfTextExtractionError):
        parse_pdf(tmp_path / "does_not_exist.pdf")
