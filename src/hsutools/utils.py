from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Iterator

import typer

from . import __version__
from . import config


def _is_path_hidden(path: Path, root: Path) -> bool:
    """Check if any part of the relative path is hidden."""
    try:
        return any(part.startswith(".") for part in path.relative_to(root).parts)
    except ValueError:
        return path.name.startswith(".")


def resolve_directory(path: Path) -> Path:
    """Resolve and validate a directory path."""
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise typer.BadParameter(f"path does not exist: {resolved}")
    if not resolved.is_dir():
        raise typer.BadParameter(f"path is not a directory: {resolved}")
    return resolved


def resolve_path(path: Path) -> Path:
    """Resolve and validate a file or directory path."""
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise typer.BadParameter(f"path does not exist: {resolved}")
    return resolved


def iter_files(
    directory: Path,
    *,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
    extensions: set[str] | None = None,
    recursive: bool = False,
    topdown: bool = True,
) -> Iterator[Path]:
    """Iterate files in a directory with filtering.

    Args:
        directory: Root directory to iterate from.
        ignore_names: Names to skip (both files and directories).
        include_hidden: Include hidden files/directories.
        extensions: Only yield files with these extensions (lowercase, with dot).
        recursive: Recurse into subdirectories.
        topdown: For recursive mode, visit parents before children (default True).
                 Set to False for bottom-up traversal (needed for safe rename).
    """
    ignore_set = set(ignore_names or [])

    if recursive:
        for root, dirs, files in os.walk(str(directory), topdown=topdown):
            root_path = Path(root)
            # Filter directories in-place to control walk traversal
            dirs[:] = [
                d for d in dirs
                if d not in ignore_set
                and (include_hidden or not d.startswith("."))
            ]
            for filename in files:
                if filename in ignore_set:
                    continue
                if not include_hidden and filename.startswith("."):
                    continue
                file_path = root_path / filename
                if extensions and file_path.suffix.lower() not in extensions:
                    continue
                yield file_path
    else:
        for item in directory.iterdir():
            if not include_hidden and item.name.startswith("."):
                continue
            if item.name in ignore_set:
                continue
            if item.is_file():
                if extensions and item.suffix.lower() not in extensions:
                    continue
                yield item


def iter_dirs(
    directory: Path,
    *,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
    topdown: bool = True,
) -> Iterator[Path]:
    """Iterate directories with filtering.

    Args:
        directory: Root directory to iterate from.
        ignore_names: Directory names to skip.
        include_hidden: Include hidden directories.
        topdown: Visit parents before children (default True).
                 Set to False for bottom-up traversal (needed for safe rename).
    """
    ignore_set = set(ignore_names or [])
    for root, dirs, _ in os.walk(str(directory), topdown=topdown):
        root_path = Path(root)
        for d in dirs:
            if d in ignore_set:
                continue
            if not include_hidden and d.startswith("."):
                continue
            yield root_path / d


def iter_entries(
    directory: Path,
    *,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
    include_dirs: bool = False,
) -> Iterator[Path]:
    """Iterate files (and optionally directories) in a single directory.

    Args:
        directory: Directory to iterate.
        ignore_names: Names to skip.
        include_hidden: Include hidden entries.
        include_dirs: Include directories in addition to files.
    """
    ignore_set = set(ignore_names or [])
    for item in directory.iterdir():
        if not include_hidden and item.name.startswith("."):
            continue
        if item.name in ignore_set:
            continue
        if item.is_file() or (include_dirs and item.is_dir()):
            yield item


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_executable(extra_args: list[str] | None = None) -> int:
    """Invoke PyInstaller to build a single-file executable for the CLI."""
    if importlib.util.find_spec("PyInstaller") is None:
        typer.echo("PyInstaller is not installed. Add it via poetry add --group dev pyinstaller.")
        return 1

    entry_path = (config.PACKAGE_ROOT / "cli.py").resolve()
    options = list(config.PYINSTALLER_DEFAULT_OPTS)
    if extra_args:
        options.extend(extra_args)

    command = [sys.executable, "-m", "PyInstaller", *options, str(entry_path)]
    typer.echo(f"Running: {' '.join(command)}")
    result = subprocess.run(command, check=False)
    return result.returncode


__all__ = [
    "_is_path_hidden",
    "build_executable",
    "ensure_directory",
    "iter_dirs",
    "iter_entries",
    "iter_files",
    "resolve_directory",
    "resolve_path",
]
