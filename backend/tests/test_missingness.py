"""Missingness invariants: absent tests must never become 0."""

from app.services.parser import parse_text_pages


def test_catalog_gaps_are_omissions():
    report = parse_text_pages(
        [
            "Collection Date: 01/02/2024\n"
            "Hemoglobin 13.2 g/dL\n"
        ]
    )
    present = report.result_names()
    assert "Hemoglobin" in present
    for absent in ("Glucose", "Creatinine", "WBC", "TSH", "Vitamin D"):
        assert absent not in present
        assert report.get_result(absent) is None


def test_to_dict_has_no_zero_filled_missing_fields():
    report = parse_text_pages(["ALT 25 U/L"])
    payload = report.to_dict()
    names = {item["canonical_name"] for item in payload["results"]}
    assert names == {"ALT"}
    assert all(item["value"] is not None and item["value"] != "" for item in payload["results"])
