"""Persistence and transaction tests for reports / extracted results."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import ExtractedResult, Report, Test
from app.services.reports import process_and_persist_report
from app.services.storage import LocalReportStorage


def test_report_and_results_persist(
    client: TestClient, patient_id: int, fixtures_dir: Path, db_session: Session, app_env
):
    pdf_path = fixtures_dir / "multi_test_report.pdf"
    with pdf_path.open("rb") as handle:
        response = client.post(
            "/reports/parse",
            data={"patient_id": str(patient_id)},
            files={"file": ("multi_test_report.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 200
    body = response.json()
    report_id = body["report_id"]

    report = db_session.get(Report, report_id)
    assert report is not None
    assert report.patient_id == patient_id
    assert report.status == "parsed"
    assert report.storage_key
    assert report.report_date == "2024-03-15"

    storage = LocalReportStorage(get_settings().storage_path)
    assert storage.exists(report.storage_key)

    rows = db_session.execute(
        select(Test.canonical_name, ExtractedResult.value, ExtractedResult.unit)
        .join(Test, Test.id == ExtractedResult.test_id)
        .where(ExtractedResult.report_id == report_id)
    ).all()
    by_name = {name: (value, unit) for name, value, unit in rows}
    assert "Glucose" in by_name
    assert by_name["Glucose"][0] == "98"
    assert by_name["Glucose"][1].lower() == "mg/dl"
    assert "Creatinine" in by_name
    # Missing analytes are absent rows — not zeros.
    assert "TSH" not in by_name


def test_patient_report_relationship(
    client: TestClient, patient_id: int, fixtures_dir: Path, db_session: Session
):
    pdf_path = fixtures_dir / "alias_report.pdf"
    with pdf_path.open("rb") as handle:
        response = client.post(
            "/reports/parse",
            data={"patient_id": str(patient_id)},
            files={"file": ("alias_report.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 200

    count = db_session.scalar(
        select(func.count()).select_from(Report).where(Report.patient_id == patient_id)
    )
    assert count == 1


def test_transaction_rollback_on_failure(
    client: TestClient,
    patient_id: int,
    fixtures_dir: Path,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    app_env,
):
    pdf_bytes = (fixtures_dir / "multi_test_report.pdf").read_bytes()
    storage = LocalReportStorage(get_settings().storage_path)

    def boom(_db):
        raise RuntimeError("simulated persistence failure")

    monkeypatch.setattr("app.services.reports._test_id_map", boom)

    with pytest.raises(RuntimeError, match="simulated persistence failure"):
        process_and_persist_report(
            db_session,
            patient_id=patient_id,
            filename="multi_test_report.pdf",
            content_type="application/pdf",
            data=pdf_bytes,
            storage=storage,
        )

    # New session view of DB — no leftover reports/results; no orphaned files.
    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(Report)) == 0
    assert db_session.scalar(select(func.count()).select_from(ExtractedResult)) == 0
    assert list(get_settings().storage_path.rglob("*.pdf")) == []


def test_persisted_missing_tests_never_zero(
    client: TestClient, patient_id: int, fixtures_dir: Path, db_session: Session
):
    pdf_path = fixtures_dir / "date_only_sparse.pdf"
    with pdf_path.open("rb") as handle:
        response = client.post(
            "/reports/parse",
            data={"patient_id": str(patient_id)},
            files={"file": ("date_only_sparse.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["results"] == []
    assert body["report_date"] == "2025-09-03"

    report_id = body["report_id"]
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(ExtractedResult)
            .where(ExtractedResult.report_id == report_id)
        )
        == 0
    )
