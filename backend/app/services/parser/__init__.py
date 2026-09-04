"""Deterministic medical/lab PDF parser (no AI, no OCR)."""

from .models import ExtractedResult, ParsedReport, SourceRef, PARSER_VERSION
from .parser import parse_pdf, parse_pdf_bytes, parse_text_pages

__all__ = [
    "PARSER_VERSION",
    "ExtractedResult",
    "ParsedReport",
    "SourceRef",
    "parse_pdf",
    "parse_pdf_bytes",
    "parse_text_pages",
]
