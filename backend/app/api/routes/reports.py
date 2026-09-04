"""Report upload and parse routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.schemas import ErrorResponse, PersistedReportSchema
from app.services.reports import ReportProcessingError, process_and_persist_report

router = APIRouter()


@router.post(
    "/parse",
    response_model=PersistedReportSchema,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
    },
    summary="Upload a lab PDF for a patient, parse, and persist results",
)
async def parse_report(
    patient_id: int = Form(..., description="Existing patient ID"),
    file: UploadFile = File(..., description="Digital medical/lab PDF"),
    db: Session = Depends(get_db),
) -> PersistedReportSchema:
    """Accept a PDF for a patient, run the deterministic parser, persist results.

    Missing tests are omitted from ``results`` and are never filled with 0.
    PDF bytes are stored on local disk (not in PostgreSQL).
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
        return process_and_persist_report(
            db,
            patient_id=patient_id,
            filename=file.filename,
            content_type=file.content_type,
            data=data,
            settings=settings,
        )
    except ReportProcessingError as exc:
        message = str(exc)
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=code, detail=message) from exc
