"""Generate committed PDF fixtures used by parser tests."""

from pathlib import Path
import sys

_TESTS_DIR = Path(__file__).resolve().parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from helpers_pdf import write_fixture

FIXTURES = _TESTS_DIR / "fixtures"


def main() -> None:
    write_fixture(
        FIXTURES / "multi_test_report.pdf",
        [
            "Fixture Lab Report",
            "Collection Date: 15/03/2024",
            "Hemoglobin 13.5 g/dL",
            "WBC 6.2 x10^3/uL",
            "Glucose (FBS) 98 mg/dL",
            "Creatinine 0.9 mg/dL",
            "HbA1c 5.4 %",
        ],
    )
    write_fixture(
        FIXTURES / "alias_report.pdf",
        [
            "Report Date: 2024-07-01",
            "Hgb 12.1 g/dL",
            "FBS 110 mg/dL",
            "SGPT 32 U/L",
            "TSH 2.1 uIU/mL",
        ],
    )
    write_fixture(
        FIXTURES / "date_only_sparse.pdf",
        [
            "Collected on: 03-Sep-2025",
            "Patient notes: fixture only",
            "No catalogued analytes listed here",
        ],
    )
    write_fixture(
        FIXTURES / "empty_text.pdf",
        [],
    )
    # Minimal valid-looking PDF with a blank content stream already covered;
    # also write a clearly malformed file for negative tests.
    (FIXTURES / "malformed.pdf").write_bytes(b"this is not a pdf")
    print(f"Wrote fixtures under {FIXTURES}")


if __name__ == "__main__":
    main()
