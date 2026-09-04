"""Catalog alias resolution tests."""

from app.services.parser.catalog import resolve_alias


def test_canonical_and_common_aliases():
    assert resolve_alias("Hemoglobin") == "Hemoglobin"
    assert resolve_alias("Hgb") == "Hemoglobin"
    assert resolve_alias("Hb") == "Hemoglobin"
    assert resolve_alias("FBS") == "Glucose"
    assert resolve_alias("glucose (fbs)") == "Glucose"
    assert resolve_alias("SGPT") == "ALT"
    assert resolve_alias("A1c") == "HbA1c"


def test_unknown_alias_returns_none():
    assert resolve_alias("Not A Real Analyte") is None
    assert resolve_alias("") is None
