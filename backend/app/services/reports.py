"""Report processing service — validates uploads, parses, and persists results.

Does not invent or alter extracted medical values.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.db.models import ExtractedResult, Report, ReportStatus, Test
from app.db.seed import seed_canonical_tests
from app.models.schemas import (
    ExtractedResultSchema,
    ParsedReportSchema,
    PersistedReportSchema,
    SourceRefSchema,
)
from app.services.parser import parse_pdf_bytes
from app.services.parser.text_extract import PdfTextExtractionError
from app.services.patients import PatientNotFoundError, get_patient
from app.services.storage import (
    LocalReportStorage,
    ReportStorage,
    build_report_storage_key,
)

PDF_MAGIC = b"%PDF"
_PDF_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    }
)


class ReportProcessingError(ValueError):
    """Raised when an upload cannot be accepted or parsed."""


def is_pdf_bytes(data: bytes) -> bool:
    return bool(data) and data.lstrip().startswith(PDF_MAGIC)


def validate_pdf_upload(
    *,
    filename: str | None,
    content_type: str | None,
    data: bytes,
    max_upload_bytes: int,
) -> None:
    if not data:
        raise ReportProcessingError("Uploaded file is empty.")

    if len(data) > max_upload_bytes:
        raise ReportProcessingError(
            f"Uploaded file exceeds maximum size of {max_upload_bytes} bytes."
        )

    name = (filename or "").lower().strip()
    ctype = (content_type or "").lower().split(";")[0].strip()
    has_pdf_extension = name.endswith(".pdf")
    has_pdf_content_type = ctype in _PDF_CONTENT_TYPES or ctype == ""

    if not has_pdf_extension and ctype not in {"application/pdf", "application/x-pdf"}:
        raise ReportProcessingError(
            "Only PDF uploads are accepted (expected .pdf filename or application/pdf)."
        )

    if ctype and ctype not in _PDF_CONTENT_TYPES and not has_pdf_extension:
        raise ReportProcessingError(
            f"Unsupported content type '{content_type}'. Only PDF is accepted."
        )

    if not has_pdf_content_type and not has_pdf_extension:
        raise ReportProcessingError("Only PDF uploads are accepted.")

    if not is_pdf_bytes(data):
        raise ReportProcessingError("File content is not a valid PDF.")


def process_pdf_bytes(data: bytes) -> ParsedReportSchema:
    """Parse only (no persistence). Values are mapped faithfully from the parser."""
    try:
        parsed = parse_pdf_bytes(data)
    except PdfTextExtractionError as exc:
        raise ReportProcessingError(str(exc)) from exc
    return ParsedReportSchema.from_parser(parsed)


def _get_storage(settings: Settings | None = None) -> ReportStorage:
    cfg = settings or get_settings()
    return LocalReportStorage(cfg.storage_path)


def _test_id_map(db: Session) -> dict[str, int]:
    seed_canonical_tests(db, commit=False)
    rows = db.scalars(select(Test)).all()
    return {row.canonical_name: row.id for row in rows}


def _to_persisted_schema(
    report: Report,
    *,
    pages_text: list[str] | None = None,
    warnings: list[str] | None = None,
) -> PersistedReportSchema:
    results: list[ExtractedResultSchema] = []
    for row in report.extracted_results:
        results.append(
            ExtractedResultSchema(
                canonical_name=row.test.canonical_name if row.test else "",
                raw_name=row.raw_name,
                value=row.value,
                value_numeric=row.value_numeric,
                unit=row.unit,
                confidence=row.confidence,
                method=row.method,
                source=SourceRefSchema(
                    page=row.source_page,
                    line=row.source_line,
                    line_number=row.source_line_number,
                ),
                test_id=row.test_id,
                id=row.id,
            )
        )
    return PersistedReportSchema(
        report_id=report.id,
        patient_id=report.patient_id,
        status=report.status,
        original_filename=report.original_filename,
        storage_key=report.storage_key,
        parser_version=report.parser_version or "",
        report_date=report.report_date,
        report_date_raw=report.report_date_raw,
        report_date_confidence=report.report_date_confidence,
        report_date_method=report.report_date_method,
        results=results,
        pages_text=pages_text or [],
        warnings=warnings or [],
        error_message=report.error_message,
    )


def process_and_persist_report(
    db: Session,
    *,
    patient_id: int,
    filename: str | None,
    content_type: str | None,
    data: bytes,
    settings: Settings | None = None,
    storage: ReportStorage | None = None,
) -> PersistedReportSchema:
    """Validate, parse, store PDF on disk, and persist report + extracted results.

    On failure after DB writes begin, the transaction is rolled back and any
    written file is removed so state is not left corrupted.
    """
    cfg = settings or get_settings()
    store = storage or _get_storage(cfg)

    validate_pdf_upload(
        filename=filename,
        content_type=content_type,
        data=data,
        max_upload_bytes=cfg.max_upload_bytes,
    )

    try:
        get_patient(db, patient_id)
    except PatientNotFoundError as exc:
        raise ReportProcessingError(str(exc)) from exc

    # Parse before opening a persistence transaction so invalid PDFs that pass
    # magic-byte checks still avoid partial DB writes when possible.
    try:
        parsed = parse_pdf_bytes(data)
    except PdfTextExtractionError as exc:
        raise ReportProcessingError(str(exc)) from exc

    parsed_schema = ParsedReportSchema.from_parser(parsed)
    storage_key: str | None = None
    report: Report | None = None

    try:
        report = Report(
            patient_id=patient_id,
            status=ReportStatus.processing.value,
            original_filename=filename,
            content_type=content_type,
            parser_version=parsed_schema.parser_version,
            report_date=parsed_schema.report_date,
            report_date_raw=parsed_schema.report_date_raw,
            report_date_confidence=parsed_schema.report_date_confidence,
            report_date_method=parsed_schema.report_date_method,
        )
        db.add(report)
        db.flush()  # allocate report.id

        storage_key = build_report_storage_key(
            patient_id, report.id, filename or "report.pdf"
        )
        store.save(storage_key, data)
        report.storage_key = storage_key

        name_to_id = _test_id_map(db)
        for item in parsed_schema.results:
            test_id = name_to_id.get(item.canonical_name)
            if test_id is None:
                # Ensure unexpected canonical names can still be stored.
                test = Test(canonical_name=item.canonical_name)
                db.add(test)
                db.flush()
                test_id = test.id
                name_to_id[item.canonical_name] = test_id

            db.add(
                ExtractedResult(
                    report_id=report.id,
                    test_id=test_id,
                    raw_name=item.raw_name,
                    value=item.value,
                    value_numeric=item.value_numeric,
                    unit=item.unit,
                    confidence=item.confidence,
                    method=item.method,
                    source_page=item.source.page,
                    source_line=item.source.line,
                    source_line_number=item.source.line_number,
                )
            )

        report.status = ReportStatus.parsed.value
        db.commit()
        db.refresh(report)
        report = db.scalar(
            select(Report)
            .where(Report.id == report.id)
            .options(
                selectinload(Report.extracted_results).selectinload(ExtractedResult.test)
            )
        )
        assert report is not None
        return _to_persisted_schema(
            report,
            pages_text=parsed_schema.pages_text,
            warnings=parsed_schema.warnings,
        )
    except Exception:
        db.rollback()
        if storage_key is not None:
            store.delete(storage_key)
        raise


def count_reports_for_patient(db: Session, patient_id: int) -> int:
    from sqlalchemy import func

    return int(
        db.scalar(
            select(func.count()).select_from(Report).where(Report.patient_id == patient_id)
        )
        or 0
    )


def list_extracted_results_for_report(db: Session, report_id: int) -> list[ExtractedResult]:
    stmt = (
        select(ExtractedResult)
        .where(ExtractedResult.report_id == report_id)
        .options(selectinload(ExtractedResult.test))
        .order_by(ExtractedResult.id.asc())
    )
    return list(db.scalars(stmt).all())
