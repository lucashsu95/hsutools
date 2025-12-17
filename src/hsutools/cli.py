from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from . import __version__
from .config import DEFAULT_IGNORE_NAMES, DEFAULT_OUTPUT_FILE
from .core import categorize_files, convert_docx_directory, generate_path_md, replace_names
from .utils import build_executable, resolve_directory

app = typer.Typer(help="hsutools: utilities for paths, renaming, and conversions.")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"hsutools {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(  # noqa: B008
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Root callback to support global options."""


@app.command()
def cpath(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help="Target directory."),
    output: str = typer.Option(DEFAULT_OUTPUT_FILE, help="Output markdown file name."),
    max_depth: Optional[int] = typer.Option(None, help="Limit traversal depth (None for unlimited)."),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help="Names to ignore in the tree output.",
    ),
) -> None:
    """Generate a markdown tree listing for the given directory."""
    directory = resolve_directory(path)
    output_path = generate_path_md(directory, output_file=output, ignore_names=ignore or DEFAULT_IGNORE_NAMES, max_depth=max_depth)
    typer.echo(f"Created {output_path}")


@app.command()
def filem(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help="Directory to manage."),
    mode: str = typer.Option(
        "date",
        "--mode",
        "-m",
        case_sensitive=False,
        help="Grouping strategy: date | prefix | suffix.",
    ),
    prefix: Optional[str] = typer.Option(None, help="Prefix bucket name when mode=prefix."),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help="Names to ignore.",
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        is_flag=True,
        help="Include hidden files.",
    ),
) -> None:
    """Categorize files by date, prefix, or suffix."""
    mode_value = mode.lower()
    if mode_value not in {"date", "prefix", "suffix"}:
        raise typer.BadParameter("mode must be one of: date, prefix, suffix")

    directory = resolve_directory(path)
    moved = categorize_files(
        directory,
        mode=mode_value,  # type: ignore[arg-type]
        prefix=prefix,
        ignore_names=ignore or DEFAULT_IGNORE_NAMES,
        include_hidden=include_hidden,
    )
    if not moved:
        typer.echo("No files were moved (check ignore filters or mode).")
    else:
        typer.echo(f"Moved {len(moved)} files.")


@app.command()
def rename(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help="Directory to operate."),
    find_text: str = typer.Option(..., "--find", help="Text to replace."),
    replace_text: str = typer.Option(..., "--replace", help="Replacement text."),
    include_dirs: bool = typer.Option(
        False,
        "--include-dirs",
        is_flag=True,
        help="Allow renaming directories as well.",
    ),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help="Names to ignore.",
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        is_flag=True,
        help="Include hidden entries.",
    ),
) -> None:
    """Batch rename file or directory names by replacing text."""
    directory = resolve_directory(path)
    updated = replace_names(
        directory,
        find_text=find_text,
        replace_text=replace_text,
        include_dirs=include_dirs,
        ignore_names=ignore or DEFAULT_IGNORE_NAMES,
        include_hidden=include_hidden,
    )
    if not updated:
        typer.echo("No entries matched the criteria.")
    else:
        typer.echo(f"Renamed {len(updated)} entries.")


@app.command()
def topdf(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help="Directory containing .docx files."),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help="Names to ignore.",
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        is_flag=True,
        help="Include hidden files.",
    ),
) -> None:
    """Convert .docx files in the directory to .pdf using docx2pdf."""
    directory = resolve_directory(path)
    converted = convert_docx_directory(
        directory,
        ignore_names=ignore or DEFAULT_IGNORE_NAMES,
        include_hidden=include_hidden,
    )
    if not converted:
        typer.echo("No .docx files found to convert.")
    else:
        typer.echo(f"Converted {len(converted)} file(s).")


@app.command("build-exe")
def build_exe(
    extra: list[str] = typer.Option(
        None,
        "--extra-arg",
        help="Extra arguments forwarded to PyInstaller.",
    ),
) -> None:
    """Build a single-file executable via PyInstaller (optional)."""
    code = build_executable(extra_args=extra)
    raise typer.Exit(code)


if __name__ == "__main__":
    app()
