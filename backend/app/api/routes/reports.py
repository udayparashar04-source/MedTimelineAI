"""Report upload and parse routes."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.models.schemas import ErrorResponse, ParsedReportSchema
from app.services.reports import ReportProcessingError, process_pdf_bytes, validate_pdf_upload

router = APIRouter()


@router.post(
    "/parse",
    response_model=ParsedReportSchema,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
    },
    summary="Upload a lab PDF and return deterministic parse results",
)
async def parse_report(
    file: UploadFile = File(..., description="Digital medical/lab PDF"),
) -> ParsedReportSchema:
    """Accept a PDF, run the existing deterministic parser, return structured JSON.

    Missing tests are omitted from ``results`` and are never filled with 0.
    Extracted values are returned as produced by the parser without alteration.
    """
    settings = get_settings()
    data = await file.read()

    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Uploaded file exceeds maximum size of "
                f"{settings.max_upload_bytes} bytes."
            ),
        )

    try:
        validate_pdf_upload(
            filename=file.filename,
            content_type=file.content_type,
            data=data,
            max_upload_bytes=settings.max_upload_bytes,
        )
        return process_pdf_bytes(data)
    except ReportProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
