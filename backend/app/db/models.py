"""ORM models for patients, reports, tests, and extracted results."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    parsed = "parsed"
    needs_review = "needs_review"
    needs_ocr = "needs_ocr"
    failed = "failed"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    reports: Mapped[list[Report]] = relationship(back_populates="patient")


class Test(Base):
    """Canonical lab test definitions (aliases live in the parser catalog)."""

    __test__ = False  # prevent pytest from collecting this ORM model
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    extracted_results: Mapped[list[ExtractedResult]] = relationship(
        back_populates="test"
    )


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=ReportStatus.pending.value, index=True
    )
    original_filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    storage_key: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    parser_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    report_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    report_date_raw: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    report_date_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    report_date_method: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    patient: Mapped[Patient] = relationship(back_populates="reports")
    extracted_results: Mapped[list[ExtractedResult]] = relationship(
        back_populates="report",
        cascade="all, delete-orphan",
    )


class ExtractedResult(Base):
    """One extracted observation. Missing tests are never stored as 0."""

    __tablename__ = "extracted_results"
    __table_args__ = (
        UniqueConstraint("report_id", "test_id", name="uq_report_test"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_id: Mapped[int] = mapped_column(
        ForeignKey("tests.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    raw_name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    value_numeric: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(64), nullable=False)
    source_page: Mapped[int] = mapped_column(Integer, nullable=False)
    source_line: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    report: Mapped[Report] = relationship(back_populates="extracted_results")
    test: Mapped[Test] = relationship(back_populates="extracted_results")
