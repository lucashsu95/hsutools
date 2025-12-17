from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Literal

from ..config import FILE_SUFFIX_BUCKETS
from ..utils import ensure_directory, iter_files

FileCategoryMode = Literal["date", "prefix", "suffix"]


def _by_date(files: List[Path]) -> List[Path]:
    moved: List[Path] = []
    for file in files:
        date_folder = datetime.fromtimestamp(file.stat().st_mtime).strftime("%m%d")
        target_dir = file.parent / date_folder
        ensure_directory(target_dir)
        target = target_dir / file.name
        file.rename(target)
        moved.append(target)
    return moved


def _by_prefix(files: List[Path], prefix: str | None) -> List[Path]:
    moved: List[Path] = []
    for file in files:
        stem = file.stem
        bucket = prefix if prefix and stem.startswith(prefix) else stem
        target_dir = file.parent / bucket
        ensure_directory(target_dir)
        target = target_dir / file.name
        file.rename(target)
        moved.append(target)
    return moved


def _by_suffix(files: List[Path]) -> List[Path]:
    moved: List[Path] = []
    for file in files:
        extension = file.suffix.lower().lstrip(".")
        bucket = FILE_SUFFIX_BUCKETS.get(extension)
        if not bucket:
            continue
        target_dir = file.parent / bucket
        ensure_directory(target_dir)
        target = target_dir / file.name
        file.rename(target)
        moved.append(target)
    return moved


def categorize_files(
    directory: Path,
    mode: FileCategoryMode,
    *,
    prefix: str | None = None,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
) -> List[Path]:
    files = list(
        iter_files(directory, ignore_names=ignore_names, include_hidden=include_hidden)
    )
    if mode == "date":
        return _by_date(files)
    if mode == "prefix":
        return _by_prefix(files, prefix)
    if mode == "suffix":
        return _by_suffix(files)
    raise ValueError(f"Unsupported mode: {mode}")


__all__ = ["categorize_files", "FileCategoryMode"]
