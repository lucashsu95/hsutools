from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from docx2pdf import convert

from ..config import DOCX_EXTENSION
from ..utils import iter_files


def convert_docx_directory(
    directory: Path,
    *,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
) -> List[Path]:
    docx_files = list(
        iter_files(
            directory,
            ignore_names=ignore_names,
            include_hidden=include_hidden,
            extensions={DOCX_EXTENSION},
        )
    )

    converted: List[Path] = []
    for docx_file in docx_files:
        pdf_path = docx_file.with_suffix(".pdf")
        convert(str(docx_file), str(pdf_path))
        converted.append(pdf_path)
    return converted


__all__ = ["convert_docx_directory"]
