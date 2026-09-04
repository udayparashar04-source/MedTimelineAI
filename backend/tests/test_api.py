"""FastAPI / HTTP API tests for health, CORS, and report parse persistence."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db.models import ExtractedResult, Report


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "MedTimelineAI"
    assert "version" in body


def test_valid_pdf_upload_returns_parser_result(
    client: TestClient, patient_id: int, fixtures_dir: Path
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

    assert body["report_id"]
    assert body["patient_id"] == patient_id
    assert body["status"] == "parsed"
    assert body["parser_version"]
    assert body["report_date"] == "2024-03-15"
    names = {item["canonical_name"] for item in body["results"]}
    assert {"Hemoglobin", "WBC", "Glucose", "Creatinine", "HbA1c"} <= names

    glucose = next(r for r in body["results"] if r["canonical_name"] == "Glucose")
    assert glucose["value"] == "98"
    assert glucose["value_numeric"] == 98.0
    assert glucose["unit"].lower() == "mg/dl"
    assert glucose["confidence"] > 0
    assert glucose["method"] == "alias_line_match"
    assert glucose["source"]["page"] == 1
    assert glucose["source"]["line"]
    assert "report_date_raw" in body
    assert "report_date_confidence" in body
    assert "report_date_method" in body


def test_alias_pdf_preserves_canonical_names(
    client: TestClient, patient_id: int, fixtures_dir: Path
):
    pdf_path = fixtures_dir / "alias_report.pdf"
    with pdf_path.open("rb") as handle:
        response = client.post(
            "/reports/parse",
            data={"patient_id": str(patient_id)},
            files={"file": ("alias_report.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 200
    body = response.json()
    names = {item["canonical_name"] for item in body["results"]}
    assert "Hemoglobin" in names
    assert "Glucose" in names
    assert "ALT" in names
    assert "Hgb" not in names
    assert "FBS" not in names


def test_malformed_pdf_returns_400(
    client: TestClient, patient_id: int, fixtures_dir: Path, db_session
):
    pdf_path = fixtures_dir / "malformed.pdf"
    with pdf_path.open("rb") as handle:
        response = client.post(
            "/reports/parse",
            data={"patient_id": str(patient_id)},
            files={"file": ("malformed.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert db_session.scalar(select(func.count()).select_from(Report)) == 0


def test_non_pdf_upload_returns_400(client: TestClient, patient_id: int, db_session):
    response = client.post(
        "/reports/parse",
        data={"patient_id": str(patient_id)},
        files={"file": ("notes.txt", b"just plain text", "text/plain")},
    )
    assert response.status_code == 400
    detail = response.json()["detail"].lower()
    assert "pdf" in detail
    assert db_session.scalar(select(func.count()).select_from(Report)) == 0


def test_missing_tests_remain_absent_never_zero(
    client: TestClient, patient_id: int, fixtures_dir: Path, db_session
):
    pdf_path = fixtures_dir / "alias_report.pdf"
    with pdf_path.open("rb") as handle:
        response = client.post(
            "/reports/parse",
            data={"patient_id": str(patient_id)},
            files={"file": ("alias_report.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 200
    body = response.json()
    names = {item["canonical_name"] for item in body["results"]}

    for absent in ("Creatinine", "Platelets", "Vitamin D"):
        assert absent not in names

    assert all(item["value"] not in (None, "") for item in body["results"])
    assert not any(
        item["canonical_name"] == "Creatinine" and item.get("value_numeric") == 0
        for item in body["results"]
    )

    report_id = body["report_id"]
    from app.db.models import Test

    rows = db_session.execute(
        select(Test.canonical_name, ExtractedResult.value_numeric)
        .join(Test, Test.id == ExtractedResult.test_id)
        .where(ExtractedResult.report_id == report_id)
    ).all()
    db_names = {name for name, _ in rows}
    assert "Creatinine" not in db_names
    assert "Platelets" not in db_names


def test_cors_allows_vite_origin(client: TestClient):
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in {200, 204}
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_invalid_patient_id_returns_404(client: TestClient, fixtures_dir: Path, db_session):
    pdf_path = fixtures_dir / "multi_test_report.pdf"
    with pdf_path.open("rb") as handle:
        response = client.post(
            "/reports/parse",
            data={"patient_id": "999999"},
            files={"file": ("multi_test_report.pdf", handle, "application/pdf")},
        )
    assert response.status_code == 404
    assert db_session.scalar(select(func.count()).select_from(Report)) == 0
