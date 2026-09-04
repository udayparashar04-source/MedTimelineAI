"""Patient API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import ErrorResponse, PatientCreate, PatientResponse
from app.services.patients import PatientNotFoundError, create_patient, get_patient, list_patients

router = APIRouter()


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_patient_endpoint(
    payload: PatientCreate,
    db: Session = Depends(get_db),
) -> PatientResponse:
    try:
        patient = create_patient(
            db, display_name=payload.display_name, notes=payload.notes
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return PatientResponse.model_validate(patient)


@router.get("", response_model=list[PatientResponse])
def list_patients_endpoint(db: Session = Depends(get_db)) -> list[PatientResponse]:
    return [PatientResponse.model_validate(p) for p in list_patients(db)]


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_patient_endpoint(
    patient_id: int,
    db: Session = Depends(get_db),
) -> PatientResponse:
    try:
        patient = get_patient(db, patient_id)
    except PatientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return PatientResponse.model_validate(patient)
