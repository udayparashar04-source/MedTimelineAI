"""Rule-based extraction of lab results from page text lines."""

from __future__ import annotations

import re
from typing import Optional

from .catalog import TEST_CATALOG, TestDefinition, build_alias_index
from .models import ExtractedResult, SourceRef

# Value then optional unit. Supports comparators and simple qualitative tokens.
_VALUE_UNIT = re.compile(
    r"^[:=\-\.\s]*"
    r"(?P<value>"
    r"(?:<=|>=|<|>)?\s*"
    r"\d+(?:[.,]\d+)?(?:\s*[x×]\s*10\s*\^?\s*-?\d+)?"
    r"|negative|positive|nil|not\s+detected|detected|trace"
    r")"
    r"(?:\s*(?P<unit>"
    r"%|g/dL|g/dl|mg/dL|mg/dl|mmol/L|mmol/l|ng/mL|ng/ml|"
    r"pg/mL|pg/ml|µIU/mL|uIU/mL|IU/mL|iu/ml|U/L|u/l|"
    r"x10\^3/µL|x10\^3/uL|10\^3/µL|10\^3/uL|"
    r"x10\^6/µL|x10\^6/uL|10\^6/µL|10\^6/uL|"
    r"cells/µL|cells/uL|/µL|/uL|mm/hr|mm/h|"
    r"mEq/L|meq/l|µg/dL|ug/dL|mcg/dL"
    r"))?"
    r"\b",
    re.IGNORECASE,
)

_STRIP_REF = re.compile(
    r"\s*(?:reference\s*range|ref\.?\s*range|biological\s*ref).*$",
    re.IGNORECASE,
)


def _normalize_numeric_token(token: str) -> Optional[float]:
    cleaned = token.strip().lower()
    for prefix in ("<=", ">=", "<", ">"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()
            break
    cleaned = cleaned.replace(",", ".")
    # Ignore scientific multiplier suffixes for numeric field (value text kept full).
    cleaned = re.split(r"[x×]", cleaned, maxsplit=1)[0].strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _confidence(value: str, unit: Optional[str], value_numeric: Optional[float]) -> float:
    if value_numeric is not None and unit:
        return 0.95
    if value_numeric is not None:
        return 0.80
    if value and unit:
        return 0.75
    if value:
        return 0.65
    return 0.0


def _match_alias(
    line: str,
    alias_index: list[tuple[str, str]],
) -> Optional[tuple[str, str, str]]:
    """Return (canonical, raw_name, remainder) if a catalog alias anchors the line."""
    stripped = line.strip()
    if not stripped:
        return None
    lower = stripped.lower()
    for alias, canonical in alias_index:
        # Optional leading list markers / numbers, then alias at a word boundary.
        # Use (?!\w) so aliases ending in '+' (e.g. Na+) still match.
        pattern = re.compile(
            rf"^(?P<prefix>[\d\.\)\-\*]+\s*)?(?P<alias>{re.escape(alias)})(?!\w)",
            re.IGNORECASE,
        )
        match = pattern.match(lower)
        if not match:
            continue
        alias_start = match.start("alias")
        alias_end = match.end("alias")
        raw_name = stripped[alias_start:alias_end]
        remainder = stripped[alias_end:]
        return canonical, raw_name, remainder
    return None


def extract_results_from_pages(
    pages: list[str],
    catalog: tuple[TestDefinition, ...] = TEST_CATALOG,
) -> tuple[list[ExtractedResult], list[str]]:
    """Extract results from page texts.

    Missing catalog tests are omitted (never fabricated as 0).
    Only the first hit per canonical name is kept (deterministic).
    """
    alias_index = build_alias_index(catalog)
    found: dict[str, ExtractedResult] = {}
    warnings: list[str] = []

    for page_index, page_text in enumerate(pages, start=1):
        lines = page_text.splitlines()
        if not lines and page_text.strip():
            lines = [page_text]
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            matched = _match_alias(line, alias_index)
            if not matched:
                continue
            canonical, raw_name, remainder = matched
            if canonical in found:
                continue

            remainder = _STRIP_REF.sub("", remainder).strip()
            value_match = _VALUE_UNIT.match(remainder)
            if not value_match:
                warnings.append(
                    f"Recognized '{canonical}' on page {page_index} "
                    f"line {line_number} but no value could be extracted."
                )
                continue

            value_raw = value_match.group("value").strip()
            # Normalize decimal comma in displayed value only for numeric path;
            # keep original token text otherwise.
            value_text = re.sub(r"\s+", " ", value_raw)
            unit = value_match.group("unit")
            if unit:
                unit = unit.strip()
            value_numeric = _normalize_numeric_token(value_text)

            # Guard: never invent a numeric zero for non-numeric/missing content.
            if value_numeric is None and value_text in {"", "-", "—", "n/a", "na"}:
                warnings.append(
                    f"Skipping empty/placeholder value for '{canonical}' "
                    f"on page {page_index}."
                )
                continue

            confidence = _confidence(value_text, unit, value_numeric)
            found[canonical] = ExtractedResult(
                canonical_name=canonical,
                raw_name=raw_name.strip(),
                value=value_text,
                value_numeric=value_numeric,
                unit=unit,
                confidence=confidence,
                method="alias_line_match",
                source=SourceRef(
                    page=page_index,
                    line=line.strip(),
                    line_number=line_number,
                ),
            )

    # Stable order: catalog order, then any extras.
    ordered: list[ExtractedResult] = []
    seen: set[str] = set()
    for definition in catalog:
        result = found.get(definition.canonical_name)
        if result:
            ordered.append(result)
            seen.add(definition.canonical_name)
    for name, result in found.items():
        if name not in seen:
            ordered.append(result)

    return ordered, warnings
