"""Structured outputs for the deterministic lab PDF parser."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

PARSER_VERSION = "0.1.0"


@dataclass(frozen=True)
class SourceRef:
    """Where an extraction came from inside the PDF text layer."""

    page: int
    """1-based page number."""

    line: Optional[str] = None
    """Original source line text when available."""

    line_number: Optional[int] = None
    """1-based line index within the page text."""


@dataclass(frozen=True)
class ExtractedResult:
    """One observed lab result. Absent tests are omitted entirely (never 0)."""

    canonical_name: str
    raw_name: str
    value: str
    """Raw extracted value as text (numeric or qualitative). Never invented."""

    value_numeric: Optional[float]
    """Numeric parse of value when applicable; None for text/qualitative.
    Missing tests are not represented as 0 — they are simply not present.
    """

    unit: Optional[str]
    confidence: float
    """0.0–1.0 heuristic for match quality; not a clinical certainty claim."""

    method: str
    """Extraction method id, e.g. alias_line_match."""

    source: SourceRef


@dataclass
class ParsedReport:
    """Framework-independent parse output for future API consumption."""

    parser_version: str
    report_date: Optional[str]
    """ISO date YYYY-MM-DD when confidently detected; else None."""

    report_date_raw: Optional[str]
    report_date_confidence: Optional[float]
    report_date_method: Optional[str]
    results: list[ExtractedResult] = field(default_factory=list)
    pages_text: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def result_names(self) -> set[str]:
        return {r.canonical_name for r in self.results}

    def get_result(self, canonical_name: str) -> Optional[ExtractedResult]:
        for result in self.results:
            if result.canonical_name == canonical_name:
                return result
        return None
