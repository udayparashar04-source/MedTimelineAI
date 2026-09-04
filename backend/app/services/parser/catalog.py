"""Maintainable catalog of canonical lab tests and common aliases.

Expand by adding entries to TEST_CATALOG. Aliases are matched case-insensitively;
longer aliases are preferred over shorter ones.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestDefinition:
    canonical_name: str
    aliases: tuple[str, ...]
    """Aliases including the canonical display form when useful."""


# Initial sensible catalog — easy to extend.
TEST_CATALOG: tuple[TestDefinition, ...] = (
    TestDefinition(
        "Hemoglobin",
        ("hemoglobin", "haemoglobin", "hgb", "hb"),
    ),
    TestDefinition(
        "Hematocrit",
        ("hematocrit", "haematocrit", "hct", "pcv"),
    ),
    TestDefinition(
        "WBC",
        (
            "white blood cell count",
            "white blood cells",
            "total leucocyte count",
            "total leukocyte count",
            "tlc",
            "wbc count",
            "wbc",
        ),
    ),
    TestDefinition(
        "RBC",
        (
            "red blood cell count",
            "red blood cells",
            "total rbc count",
            "rbc count",
            "rbc",
        ),
    ),
    TestDefinition(
        "Platelets",
        (
            "platelet count",
            "platelets",
            "plt count",
            "plt",
        ),
    ),
    TestDefinition(
        "Glucose",
        (
            "fasting blood sugar",
            "fasting plasma glucose",
            "fasting glucose",
            "blood glucose",
            "glucose fasting",
            "glucose (fbs)",
            "glucose fbs",
            "fbs",
            "fpg",
            "glucose",
        ),
    ),
    TestDefinition(
        "HbA1c",
        (
            "glycated hemoglobin",
            "glycated haemoglobin",
            "glycosylated hemoglobin",
            "hemoglobin a1c",
            "haemoglobin a1c",
            "hba1c",
            "a1c",
        ),
    ),
    TestDefinition(
        "Creatinine",
        ("serum creatinine", "creatinine"),
    ),
    TestDefinition(
        "Urea",
        ("blood urea nitrogen", "blood urea", "urea nitrogen", "bun", "urea"),
    ),
    TestDefinition(
        "Total Cholesterol",
        ("total cholesterol", "serum cholesterol", "cholesterol total", "cholesterol"),
    ),
    TestDefinition(
        "HDL Cholesterol",
        ("hdl cholesterol", "hdl-c", "hdl"),
    ),
    TestDefinition(
        "LDL Cholesterol",
        ("ldl cholesterol", "ldl-c", "ldl"),
    ),
    TestDefinition(
        "Triglycerides",
        ("triglycerides", "triglyceride", "tg"),
    ),
    TestDefinition(
        "TSH",
        (
            "thyroid stimulating hormone",
            "thyroid-stimulating hormone",
            "serum tsh",
            "tsh",
        ),
    ),
    TestDefinition(
        "Vitamin D",
        (
            "25-hydroxy vitamin d",
            "25-oh vitamin d",
            "25(oh)d",
            "vitamin d 25-oh",
            "vitamin d3",
            "vitamin d",
        ),
    ),
    TestDefinition(
        "ALT",
        ("alanine aminotransferase", "sgpt", "alt"),
    ),
    TestDefinition(
        "AST",
        ("aspartate aminotransferase", "sgot", "ast"),
    ),
    TestDefinition(
        "Total Bilirubin",
        ("total bilirubin", "bilirubin total", "bilirubin"),
    ),
    TestDefinition(
        "Sodium",
        ("serum sodium", "sodium", "na+"),
    ),
    TestDefinition(
        "Potassium",
        ("serum potassium", "potassium", "k+"),
    ),
    TestDefinition(
        "Calcium",
        ("serum calcium", "calcium"),
    ),
    TestDefinition(
        "Vitamin B12",
        ("vitamin b12", "vit b12", "cobalamin", "b12"),
    ),
)


def build_alias_index(
    catalog: tuple[TestDefinition, ...] = TEST_CATALOG,
) -> list[tuple[str, str]]:
    """Return (alias_lower, canonical_name) sorted by alias length descending."""
    pairs: list[tuple[str, str]] = []
    for definition in catalog:
        for alias in definition.aliases:
            pairs.append((alias.lower().strip(), definition.canonical_name))
    pairs.sort(key=lambda item: len(item[0]), reverse=True)
    return pairs


def resolve_alias(
    raw_name: str,
    catalog: tuple[TestDefinition, ...] = TEST_CATALOG,
) -> str | None:
    """Map a raw test name to a canonical name, or None if unknown."""
    needle = raw_name.lower().strip()
    if not needle:
        return None
    for alias, canonical in build_alias_index(catalog):
        if needle == alias:
            return canonical
    return None
