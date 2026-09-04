"""Page-aware PDF text extraction using pypdf (digital text layer only)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

from pypdf import PdfReader

from .models import PARSER_VERSION

PathLike = Union[str, Path]


class PdfTextExtractionError(ValueError):
    """Raised when the input is not a usable digital PDF."""


def extract_pages_from_reader(reader: PdfReader) -> list[str]:
    """Extract plain text for each page in order. Empty pages become ''."""
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        pages.append(text if text is not None else "")
    return pages


def extract_pages_from_bytes(data: bytes) -> list[str]:
    if not data:
        raise PdfTextExtractionError("Empty PDF input.")
    try:
        reader = PdfReader(BytesIO(data))
    except Exception as exc:  # noqa: BLE001 — surface as parse error
        raise PdfTextExtractionError(f"Unable to read PDF: {exc}") from exc
    if reader.is_encrypted:
        # Try empty password; otherwise fail clearly (no OCR/bypass).
        try:
            unlocked = reader.decrypt("")
        except Exception as exc:  # noqa: BLE001
            raise PdfTextExtractionError(
                f"Encrypted PDF cannot be opened: {exc}"
            ) from exc
        if unlocked == 0:
            raise PdfTextExtractionError("Encrypted PDF is not supported.")
    return extract_pages_from_reader(reader)


def extract_pages_from_path(path: PathLike) -> list[str]:
    file_path = Path(path)
    if not file_path.is_file():
        raise PdfTextExtractionError(f"PDF file not found: {file_path}")
    return extract_pages_from_bytes(file_path.read_bytes())


def extract_pages_from_stream(stream: BinaryIO) -> list[str]:
    data = stream.read()
    return extract_pages_from_bytes(data)


def extraction_metadata() -> dict[str, str]:
    return {
        "parser_version": PARSER_VERSION,
        "engine": "pypdf",
        "ocr": "disabled",
        "ai": "disabled",
    }
