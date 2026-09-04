"""Deterministic report/collection date detection from PDF text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class DetectedDate:
    iso_date: str
    raw: str
    confidence: float
    method: str
    page: int
    line: str
    line_number: int


_MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

_LABEL = (
    r"(?:collection\s*date|collected\s*(?:on|date)?|sample\s*date|"
    r"specimen\s*date|report\s*date|reported\s*(?:on|date)?|"
    r"date\s*of\s*(?:collection|report|sample)|date)"
)

# Labeled dates preferred.
_LABELED_PATTERNS: tuple[tuple[re.Pattern[str], str, float], ...] = (
    (
        re.compile(
            rf"(?P<label>{_LABEL})\s*[:\-]?\s*"
            r"(?P<d>\d{1,2})[\/\-.](?P<m>\d{1,2})[\/\-.](?P<y>\d{4})\b",
            re.IGNORECASE,
        ),
        "labeled_dmy",
        0.95,
    ),
    (
        re.compile(
            rf"(?P<label>{_LABEL})\s*[:\-]?\s*"
            r"(?P<y>\d{4})[\/\-.](?P<m>\d{1,2})[\/\-.](?P<d>\d{1,2})\b",
            re.IGNORECASE,
        ),
        "labeled_ymd",
        0.95,
    ),
    (
        re.compile(
            rf"(?P<label>{_LABEL})\s*[:\-]?\s*"
            r"(?P<d>\d{1,2})[\s\-]+(?P<mon>[A-Za-z]{3,9})[\s\-,]+(?P<y>\d{4})\b",
            re.IGNORECASE,
        ),
        "labeled_d_mon_y",
        0.93,
    ),
    (
        re.compile(
            rf"(?P<label>{_LABEL})\s*[:\-]?\s*"
            r"(?P<mon>[A-Za-z]{3,9})\s+(?P<d>\d{1,2}),?\s+(?P<y>\d{4})\b",
            re.IGNORECASE,
        ),
        "labeled_mon_d_y",
        0.93,
    ),
)

# Unlabeled fallback — lower confidence; first plausible date wins.
_UNLABELED_PATTERNS: tuple[tuple[re.Pattern[str], str, float], ...] = (
    (
        re.compile(r"\b(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})\b"),
        "unlabeled_iso",
        0.55,
    ),
    (
        re.compile(r"\b(?P<d>\d{1,2})[\/\-](?P<m>\d{1,2})[\/\-](?P<y>\d{4})\b"),
        "unlabeled_dmy",
        0.50,
    ),
)


def _to_iso(year: int, month: int, day: int) -> Optional[str]:
    try:
        return datetime(year, month, day).date().isoformat()
    except ValueError:
        return None


def _from_month_name(mon: str) -> Optional[int]:
    return _MONTHS.get(mon.lower().strip("."))


def _iso_from_match(match: re.Match[str], method: str) -> Optional[tuple[str, str]]:
    groups = match.groupdict()
    raw = match.group(0)
    if "mon" in groups and groups.get("mon"):
        month = _from_month_name(groups["mon"])
        if month is None:
            return None
        iso = _to_iso(int(groups["y"]), month, int(groups["d"]))
    elif method.endswith("ymd") or method == "unlabeled_iso":
        iso = _to_iso(int(groups["y"]), int(groups["m"]), int(groups["d"]))
    else:
        # Default numeric forms treated as D/M/Y (common on lab reports outside US).
        iso = _to_iso(int(groups["y"]), int(groups["m"]), int(groups["d"]))
    if iso is None:
        return None
    return iso, raw


def detect_report_date(pages: list[str]) -> Optional[DetectedDate]:
    """Detect a single report/collection date from page texts.

    Prefers explicitly labeled dates. Does not invent a date when none is found.
    """
    labeled_hits: list[DetectedDate] = []
    unlabeled_hits: list[DetectedDate] = []

    for page_index, page_text in enumerate(pages, start=1):
        lines = page_text.splitlines() or [page_text]
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            for pattern, method, confidence in _LABELED_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                parsed = _iso_from_match(match, method)
                if not parsed:
                    continue
                iso, raw = parsed
                labeled_hits.append(
                    DetectedDate(
                        iso_date=iso,
                        raw=raw,
                        confidence=confidence,
                        method=method,
                        page=page_index,
                        line=line.strip(),
                        line_number=line_number,
                    )
                )
            for pattern, method, confidence in _UNLABELED_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                parsed = _iso_from_match(match, method)
                if not parsed:
                    continue
                iso, raw = parsed
                unlabeled_hits.append(
                    DetectedDate(
                        iso_date=iso,
                        raw=raw,
                        confidence=confidence,
                        method=method,
                        page=page_index,
                        line=line.strip(),
                        line_number=line_number,
                    )
                )

    if labeled_hits:
        # Prefer collection-oriented labels slightly by keeping first high-confidence hit
        # in document order (deterministic).
        labeled_hits.sort(key=lambda d: (-d.confidence, d.page, d.line_number))
        return labeled_hits[0]

    if unlabeled_hits:
        unlabeled_hits.sort(key=lambda d: (-d.confidence, d.page, d.line_number))
        return unlabeled_hits[0]

    return None
