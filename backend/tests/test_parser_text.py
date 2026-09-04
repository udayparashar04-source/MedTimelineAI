"""Text-level parser behavior (no PDF required)."""

from app.services.parser import parse_text_pages


def test_successful_multi_test_extraction():
    report = parse_text_pages(
        [
            "Collection Date: 15/03/2024\n"
            "Hemoglobin 13.5 g/dL\n"
            "WBC 6.2 x10^3/uL\n"
            "Glucose (FBS) 98 mg/dL\n"
            "Creatinine 0.9 mg/dL\n"
        ]
    )
    assert report.report_date == "2024-03-15"
    names = report.result_names()
    assert names == {"Hemoglobin", "WBC", "Glucose", "Creatinine"}

    hb = report.get_result("Hemoglobin")
    assert hb is not None
    assert hb.value == "13.5"
    assert hb.value_numeric == 13.5
    assert hb.unit.lower() == "g/dl"
    assert hb.source.page == 1
    assert hb.source.line is not None
    assert "Hemoglobin" in hb.source.line
    assert hb.method == "alias_line_match"
    assert 0.0 < hb.confidence <= 1.0


def test_aliases_normalize_to_canonical_names():
    report = parse_text_pages(
        [
            "Hgb 12.1 g/dL\n"
            "FBS 110 mg/dL\n"
            "SGPT 32 U/L\n"
        ]
    )
    assert report.get_result("Hemoglobin") is not None
    assert report.get_result("Glucose") is not None
    assert report.get_result("ALT") is not None
    assert report.get_result("Hgb") is None
    assert report.get_result("FBS") is None
    assert report.get_result("SGPT") is None


def test_missing_tests_are_absent_not_zero():
    report = parse_text_pages(["Hemoglobin 13.5 g/dL"])
    assert report.get_result("Hemoglobin") is not None
    # Not present in text — must not appear, and must not be fabricated as 0.
    assert report.get_result("Glucose") is None
    assert report.get_result("Creatinine") is None
    for result in report.results:
        assert result.value_numeric != 0 or result.value.strip() in {"0", "0.0", "0.00"}
    # Explicitly: absent Glucose is not a zero result.
    assert all(r.canonical_name != "Glucose" for r in report.results)


def test_empty_pages_yield_no_results():
    report = parse_text_pages([""])
    assert report.results == []
    assert report.report_date is None
    assert any("empty" in w.lower() for w in report.warnings)


def test_no_pages_yield_no_results():
    report = parse_text_pages([])
    assert report.results == []
    assert report.report_date is None


def test_values_with_units_and_qualitative():
    report = parse_text_pages(
        [
            "Total Cholesterol 180 mg/dL\n"
            "Vitamin D 28 ng/mL\n"
        ]
    )
    chol = report.get_result("Total Cholesterol")
    assert chol is not None
    assert chol.value_numeric == 180.0
    assert chol.unit.lower() == "mg/dl"

    vit = report.get_result("Vitamin D")
    assert vit is not None
    assert vit.unit.lower() == "ng/ml"


def test_placeholder_value_not_invented_as_zero():
    report = parse_text_pages(["Creatinine —"])
    assert report.get_result("Creatinine") is None


def test_source_page_across_multiple_pages():
    report = parse_text_pages(
        [
            "Collection Date: 01/01/2024\nHemoglobin 14 g/dL",
            "Glucose 90 mg/dL",
        ]
    )
    assert report.get_result("Hemoglobin").source.page == 1
    assert report.get_result("Glucose").source.page == 2
