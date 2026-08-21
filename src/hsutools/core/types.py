from __future__ import annotations

from pathlib import Path
from typing import NamedTuple


class FileOperationResult(NamedTuple):
    """Result of a single file operation (rename, move, delete, etc.)."""

    path: Path
    success: bool
    error: str | None = None
    detail: str | None = None


class OperationStats(NamedTuple):
    """Aggregated statistics for a batch operation."""

    total: int
    succeeded: int
    failed: int
    skipped: int = 0


class FileConversionResult(NamedTuple):
    """Result of a file conversion operation (e.g., format change, encoding)."""

    path: Path
    success: bool
    content_changed: bool = False
    name_changed: bool = False
    new_path: Path | None = None
    backup_path: Path | None = None
    error: str | None = None
