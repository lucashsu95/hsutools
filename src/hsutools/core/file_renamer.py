from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


def replace_names(
    directory: Path,
    *,
    find_text: str,
    replace_text: str,
    include_dirs: bool = False,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
) -> List[Path]:
    ignore = set(ignore_names or [])
    updated: List[Path] = []

    for entry in directory.iterdir():
        if not include_hidden and entry.name.startswith("."):
            continue
        if entry.name in ignore:
            continue
        if entry.is_file() or (include_dirs and entry.is_dir()):
            if find_text not in entry.name:
                continue
            if entry.is_file():
                new_name = entry.stem.replace(find_text, replace_text) + entry.suffix
            else:
                new_name = entry.name.replace(find_text, replace_text)
            target = entry.with_name(new_name)
            entry.rename(target)
            updated.append(target)
    return updated


__all__ = ["replace_names"]
