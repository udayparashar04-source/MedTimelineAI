"""Pydantic API schemas (separate from SQLAlchemy models).

These schemas serialize API data only — they never invent medical values
or fill missing tests with zeros.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.services.parser.models import ExtractedResult, ParsedReport, SourceRef


class SourceRefSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int
    line: Optional[str] = None
    line_number: Optional[int] = None

    @classmethod
    def from_parser(cls, source: SourceRef) -> SourceRefSchema:
        return cls(
            page=source.page,
            line=source.line,
            line_number=source.line_number,
        )


class ExtractedResultSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str
    raw_name: str
    value: str
    value_numeric: Optional[float] = None
    unit: Optional[str] = None
    confidence: float
    method: str
    source: SourceRefSchema
    test_id: Optional[int] = None
    id: Optional[int] = None

    @classmethod
    def from_parser(cls, result: ExtractedResult) -> ExtractedResultSchema:
        return cls(
            canonical_name=result.canonical_name,
            raw_name=result.raw_name,
            value=result.value,
            value_numeric=result.value_numeric,
            unit=result.unit,
            confidence=result.confidence,
            method=result.method,
            source=SourceRefSchema.from_parser(result.source),
        )


class ParsedReportSchema(BaseModel):
    """JSON contract for a parsed lab PDF. Absent tests are omitted from results."""

    model_config = ConfigDict(extra="forbid")

    parser_version: str
    report_date: Optional[str] = None
    report_date_raw: Optional[str] = None
    report_date_confidence: Optional[float] = None
    report_date_method: Optional[str] = None
    results: list[ExtractedResultSchema] = Field(default_factory=list)
    pages_text: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @classmethod
    def from_parser(cls, report: ParsedReport) -> ParsedReportSchema:
        return cls(
            parser_version=report.parser_version,
            report_date=report.report_date,
            report_date_raw=report.report_date_raw,
            report_date_confidence=report.report_date_confidence,
            report_date_method=report.report_date_method,
            results=[ExtractedResultSchema.from_parser(r) for r in report.results],
            pages_text=list(report.pages_text),
            warnings=list(report.warnings),
        )


class PersistedReportSchema(BaseModel):
    """Parse response after a report has been stored for a patient."""

    model_config = ConfigDict(extra="forbid")

    report_id: int
    patient_id: int
    status: str
    original_filename: Optional[str] = None
    storage_key: Optional[str] = None
    parser_version: str
    report_date: Optional[str] = None
    report_date_raw: Optional[str] = None
    report_date_confidence: Optional[float] = None
    report_date_method: Optional[str] = None
    results: list[ExtractedResultSchema] = Field(default_factory=list)
    pages_text: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error_message: Optional[str] = None


class PatientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=1, max_length=255)
    notes: Optional[str] = None


class PatientResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    display_name: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ErrorResponse(BaseModel):
    detail: str
