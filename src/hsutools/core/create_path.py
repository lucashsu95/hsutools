from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from ..config import DEFAULT_IGNORE_NAMES, DEFAULT_OUTPUT_FILE


def _link_for(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    return relative.as_posix().replace(" ", "%20")


def _render_tree(
    root: Path,
    *,
    ignore_names: Iterable[str] | None = None,
    max_depth: int | None = None,
) -> List[str]:
    ignore = set(ignore_names or [])
    lines: List[str] = []

    def dfs(current: Path, depth: int, index_stack: list[int]) -> None:
        entries = sorted(
            [p for p in current.iterdir() if p.name not in ignore],
            key=lambda p: (p.is_file(), p.name.lower()),
        )
        dir_counter = 0
        file_counter = 1
        for entry in entries:
            indent = " " * (depth - 1) * 4
            if entry.is_dir():
                dir_counter += 1
                index_stack.append(dir_counter)
                heading_level = min(depth, 6)
                lines.append(
                    f"{indent}- {'#' * heading_level} 第{'-'.join(map(str, index_stack))}章 [{entry.name}]({_link_for(entry, root)})"
                )
                if max_depth is None or depth < max_depth:
                    dfs(entry, depth + 1, index_stack)
                index_stack.pop()
            else:
                title_prefix = "-".join(map(str, index_stack))
                title = f"{title_prefix}_**{file_counter:02d}**"
                lines.append(f"{indent}- {title} [{entry.name}]({_link_for(entry, root)})")
                file_counter += 1

    dfs(root, 1, [])
    return lines


def generate_path_md(
    root: Path,
    *,
    output_file: str = DEFAULT_OUTPUT_FILE,
    ignore_names: Iterable[str] | None = None,
    max_depth: int | None = None,
) -> Path:
    """Generate a markdown listing of the directory tree."""
    ignore = set(ignore_names or DEFAULT_IGNORE_NAMES)
    lines = _render_tree(root, ignore_names=ignore, max_depth=max_depth)

    output_path = root / output_file
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


__all__ = ["generate_path_md"]
