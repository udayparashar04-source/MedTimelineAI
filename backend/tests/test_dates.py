"""Report/collection date detection tests."""

from app.services.parser.dates import detect_report_date


def test_labeled_dmy_date():
    detected = detect_report_date(["Collection Date: 15/03/2024"])
    assert detected is not None
    assert detected.iso_date == "2024-03-15"
    assert detected.confidence >= 0.9
    assert "labeled" in detected.method


def test_labeled_iso_date():
    detected = detect_report_date(["Report Date: 2024-07-01"])
    assert detected is not None
    assert detected.iso_date == "2024-07-01"


def test_labeled_month_name_date():
    detected = detect_report_date(["Collected on: 03-Sep-2025"])
    assert detected is not None
    assert detected.iso_date == "2025-09-03"


def test_no_date_returns_none():
    assert detect_report_date(["Hemoglobin 13.5 g/dL"]) is None
    assert detect_report_date([""]) is None
