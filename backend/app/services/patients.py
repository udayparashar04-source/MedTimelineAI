"""Patient CRUD service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Patient


class PatientNotFoundError(LookupError):
    pass


def create_patient(
    db: Session,
    *,
    display_name: str,
    notes: str | None = None,
) -> Patient:
    name = display_name.strip()
    if not name:
        raise ValueError("display_name is required.")
    patient = Patient(display_name=name, notes=notes)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def list_patients(db: Session) -> list[Patient]:
    stmt = select(Patient).order_by(Patient.id.asc())
    return list(db.scalars(stmt).all())


def get_patient(db: Session, patient_id: int) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise PatientNotFoundError(f"Patient {patient_id} not found.")
    return patient
