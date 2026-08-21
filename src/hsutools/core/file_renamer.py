from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from ..utils import iter_entries


def replace_names(
    directory: Path,
    *,
    find_text: str,
    replace_text: str,
    include_dirs: bool = False,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
    dry_run: bool = False,
) -> List[Path]:
    entries = list(iter_entries(
        directory,
        ignore_names=ignore_names,
        include_hidden=include_hidden,
        include_dirs=include_dirs,
    ))
    updated: List[Path] = []

    for entry in entries:
        if find_text not in entry.name:
            continue
        if entry.is_file():
            new_name = entry.stem.replace(find_text, replace_text) + entry.suffix
        else:
            new_name = entry.name.replace(find_text, replace_text)
        target = entry.with_name(new_name)
        if not dry_run:
            entry.rename(target)
        updated.append(target)
    return updated


__all__ = ["replace_names"]
