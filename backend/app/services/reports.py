"""Report processing service — validates uploads and delegates to the parser.

Does not invent or alter extracted medical values.
"""

from __future__ import annotations

from app.models.schemas import ParsedReportSchema
from app.services.parser import parse_pdf_bytes
from app.services.parser.text_extract import PdfTextExtractionError

PDF_MAGIC = b"%PDF"
_PDF_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",  # browsers sometimes use this for uploads
    }
)


class ReportProcessingError(ValueError):
    """Raised when an upload cannot be accepted or parsed."""


def is_pdf_bytes(data: bytes) -> bool:
    """True if bytes look like a PDF (magic header)."""
    return bool(data) and data.lstrip().startswith(PDF_MAGIC)


def validate_pdf_upload(
    *,
    filename: str | None,
    content_type: str | None,
    data: bytes,
    max_upload_bytes: int,
) -> None:
    """Validate size, filename/content-type hints, and PDF magic bytes."""
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
    """Run the deterministic parser and map output to the API schema unchanged."""
    try:
        parsed = parse_pdf_bytes(data)
    except PdfTextExtractionError as exc:
        raise ReportProcessingError(str(exc)) from exc

    # Faithful mapping only — no value invention or missing-test zero-fill.
    return ParsedReportSchema.from_parser(parsed)
