from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Iterator

import typer

from . import __version__
from . import config


def resolve_directory(path: Path) -> Path:
    """Resolve and validate a directory path."""
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise typer.BadParameter(f"path does not exist: {resolved}")
    if not resolved.is_dir():
        raise typer.BadParameter(f"path is not a directory: {resolved}")
    return resolved


def iter_files(
    directory: Path,
    *,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
    extensions: set[str] | None = None,
) -> Iterator[Path]:
    ignore_set = set(ignore_names or [])
    for item in directory.iterdir():
        if not include_hidden and item.name.startswith("."):
            continue
        if item.name in ignore_set:
            continue
        if item.is_file():
            if extensions and item.suffix.lower() not in extensions:
                continue
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
    "__version__",
    "build_executable",
    "ensure_directory",
    "iter_files",
    "resolve_directory",
]
