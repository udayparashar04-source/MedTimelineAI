"""Local filesystem storage for uploaded PDFs (swappable for object storage later)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ReportStorage(Protocol):
    def save(self, storage_key: str, data: bytes) -> str: ...

    def delete(self, storage_key: str) -> None: ...

    def exists(self, storage_key: str) -> bool: ...


class LocalReportStorage:
    """Store PDFs under a local directory. Keys are relative paths, not absolute."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, storage_key: str) -> Path:
        # Prevent path traversal outside the storage root.
        candidate = (self.root / storage_key).resolve()
        if not str(candidate).startswith(str(self.root)):
            raise ValueError("Invalid storage key.")
        return candidate

    def save(self, storage_key: str, data: bytes) -> str:
        path = self._resolve(storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return storage_key

    def delete(self, storage_key: str) -> None:
        path = self._resolve(storage_key)
        if path.is_file():
            path.unlink()

    def exists(self, storage_key: str) -> bool:
        return self._resolve(storage_key).is_file()


def build_report_storage_key(patient_id: int, report_id: int, filename: str) -> str:
    safe_name = Path(filename or "report.pdf").name.replace("..", "")
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"
    return f"patient_{patient_id}/report_{report_id}/{safe_name}"
