"""Public entry points for the deterministic lab PDF parser."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from .catalog import TEST_CATALOG, TestDefinition
from .dates import detect_report_date
from .models import PARSER_VERSION, ParsedReport
from .result_extract import extract_results_from_pages
from .text_extract import (
    PdfTextExtractionError,
    extract_pages_from_bytes,
    extract_pages_from_path,
)

PathLike = Union[str, Path]


def parse_text_pages(
    pages: list[str],
    *,
    catalog: tuple[TestDefinition, ...] = TEST_CATALOG,
) -> ParsedReport:
    """Parse already-extracted page texts (framework-independent, highly testable)."""
    warnings: list[str] = []
    normalized_pages = [page if page is not None else "" for page in pages]

    if not normalized_pages:
        warnings.append("No pages provided.")
        return ParsedReport(
            parser_version=PARSER_VERSION,
            report_date=None,
            report_date_raw=None,
            report_date_confidence=None,
            report_date_method=None,
            results=[],
            pages_text=[],
            warnings=warnings,
        )

    if all(not (page or "").strip() for page in normalized_pages):
        warnings.append("PDF text layer is empty; no results extracted (OCR not enabled).")

    detected = detect_report_date(normalized_pages)
    results, extract_warnings = extract_results_from_pages(
        normalized_pages, catalog=catalog
    )
    warnings.extend(extract_warnings)

    return ParsedReport(
        parser_version=PARSER_VERSION,
        report_date=detected.iso_date if detected else None,
        report_date_raw=detected.raw if detected else None,
        report_date_confidence=detected.confidence if detected else None,
        report_date_method=detected.method if detected else None,
        results=results,
        pages_text=normalized_pages,
        warnings=warnings,
    )


def parse_pdf_bytes(
    data: bytes,
    *,
    catalog: tuple[TestDefinition, ...] = TEST_CATALOG,
) -> ParsedReport:
    """Parse a digital PDF from bytes. Raises PdfTextExtractionError on bad input."""
    if data is None:
        raise PdfTextExtractionError("PDF bytes are required.")
    if not data:
        raise PdfTextExtractionError("Empty PDF input.")
    pages = extract_pages_from_bytes(data)
    return parse_text_pages(pages, catalog=catalog)


def parse_pdf(
    path: PathLike,
    *,
    catalog: tuple[TestDefinition, ...] = TEST_CATALOG,
) -> ParsedReport:
    """Parse a digital PDF from a filesystem path."""
    pages = extract_pages_from_path(path)
    return parse_text_pages(pages, catalog=catalog)


__all__ = [
    "parse_pdf",
    "parse_pdf_bytes",
    "parse_text_pages",
    "PdfTextExtractionError",
    "PARSER_VERSION",
]
