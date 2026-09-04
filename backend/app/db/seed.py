"""Seed canonical tests from the parser catalog into the tests table."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Test
from app.services.parser.catalog import TEST_CATALOG


def seed_canonical_tests(db: Session, *, commit: bool = True) -> int:
    """Insert any missing canonical test names. Returns number of rows inserted."""
    existing = set(db.scalars(select(Test.canonical_name)).all())
    inserted = 0
    for definition in TEST_CATALOG:
        if definition.canonical_name in existing:
            continue
        db.add(Test(canonical_name=definition.canonical_name))
        existing.add(definition.canonical_name)
        inserted += 1
    if inserted:
        if commit:
            db.commit()
        else:
            db.flush()
    return inserted
