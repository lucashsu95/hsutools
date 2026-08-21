from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

try:
    from docx2pdf import convert
    HAS_DOCX2PDF = True
except ImportError:
    HAS_DOCX2PDF = False

from ..config import DOCX_EXTENSION
from ..utils import iter_files


def check_docx2pdf_available() -> bool:
    return HAS_DOCX2PDF


def convert_docx_directory(
    directory: Path,
    *,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
    dry_run: bool = False,
    recursive: bool = False,
) -> List[Path]:
    docx_files = list(
        iter_files(
            directory,
            ignore_names=ignore_names,
            include_hidden=include_hidden,
            extensions={DOCX_EXTENSION},
            recursive=recursive,
        )
    )

    converted: List[Path] = []
    for docx_file in docx_files:
        pdf_path = docx_file.with_suffix(".pdf")
        if not dry_run:
            convert(str(docx_file), str(pdf_path))
        converted.append(pdf_path)
    return converted


__all__ = ["check_docx2pdf_available", "convert_docx_directory"]
