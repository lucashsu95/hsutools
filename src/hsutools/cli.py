from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from . import __version__
from .config import DEFAULT_IGNORE_NAMES, DEFAULT_OUTPUT_FILE, DOCX_EXTENSION
from .core import categorize_files, convert_docx_directory, generate_path_md, replace_names
from .utils import build_executable, resolve_directory, iter_files

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
    mode: Optional[str] = typer.Option(
        None,
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
    # If mode not provided, prompt the user to choose
    if mode is None:
        mode = typer.prompt(
            "Choose grouping strategy",
            type=typer.Choice(["date", "prefix", "suffix"], case_sensitive=False),
        )
    
    mode_value = mode.lower()
    if mode_value not in {"date", "prefix", "suffix"}:
        raise typer.BadParameter("mode must be one of: date, prefix, suffix")
    
    # If mode is prefix and prefix not provided, prompt for it
    if mode_value == "prefix" and prefix is None:
        prefix = typer.prompt("Enter the prefix to group by (or press Enter to group by each file's prefix)")
        if prefix.strip() == "":
            prefix = None

    directory = resolve_directory(path)
    
    # Preview files to be moved
    files_to_move = list(iter_files(directory, ignore_names=ignore or DEFAULT_IGNORE_NAMES, include_hidden=include_hidden))
    
    if not files_to_move:
        typer.echo("No files found to categorize.")
        return
    
    typer.echo(f"\nFound {len(files_to_move)} file(s) to categorize in mode: {mode_value}")
    typer.echo(f"Directory: {directory}")
    
    # Show confirmation
    if not typer.confirm("\nProceed with file categorization?", default=True):
        typer.echo("Operation cancelled.")
        return
    
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
        typer.echo(f"✓ Successfully moved {len(moved)} files.")


@app.command()
def rename(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help="Directory to operate."),
    find_text: Optional[str] = typer.Option(None, "--find", help="Text to replace."),
    replace_text: Optional[str] = typer.Option(None, "--replace", help="Replacement text."),
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
    # Interactive prompts if parameters not provided
    if find_text is None:
        find_text = typer.prompt("Enter text to find")
    if replace_text is None:
        replace_text = typer.prompt("Enter replacement text")
    
    directory = resolve_directory(path)
    
    # Preview matching entries
    ignore_set = set(ignore or DEFAULT_IGNORE_NAMES)
    matching_entries = []
    for entry in directory.iterdir():
        if not include_hidden and entry.name.startswith("."):
            continue
        if entry.name in ignore_set:
            continue
        if entry.is_file() or (include_dirs and entry.is_dir()):
            if find_text in entry.name:
                matching_entries.append(entry)
    
    if not matching_entries:
        typer.echo(f"No entries found containing '{find_text}'.")
        return
    
    typer.echo(f"\nFound {len(matching_entries)} entry(s) to rename:")
    typer.echo(f"Find: '{find_text}' → Replace with: '{replace_text}'\n")
    
    # Show preview (max 10 entries)
    for i, entry in enumerate(matching_entries[:10]):
        if entry.is_file():
            new_name = entry.stem.replace(find_text, replace_text) + entry.suffix
        else:
            new_name = entry.name.replace(find_text, replace_text)
        typer.echo(f"  {entry.name} → {new_name}")
    
    if len(matching_entries) > 10:
        typer.echo(f"  ... and {len(matching_entries) - 10} more")
    
    # Confirmation
    if not typer.confirm("\nProceed with rename?", default=True):
        typer.echo("Operation cancelled.")
        return
    
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
        typer.echo(f"✓ Successfully renamed {len(updated)} entries.")


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
    
    # Preview files to convert
    docx_files = list(
        iter_files(
            directory,
            ignore_names=ignore or DEFAULT_IGNORE_NAMES,
            include_hidden=include_hidden,
            extensions={DOCX_EXTENSION},
        )
    )
    
    if not docx_files:
        typer.echo("No .docx files found to convert.")
        return
    
    typer.echo(f"\nFound {len(docx_files)} .docx file(s) to convert:")
    for i, f in enumerate(docx_files[:10]):
        typer.echo(f"  {f.name}")
    if len(docx_files) > 10:
        typer.echo(f"  ... and {len(docx_files) - 10} more")
    
    # Confirmation
    if not typer.confirm("\nProceed with conversion?", default=True):
        typer.echo("Operation cancelled.")
        return
    
    converted = convert_docx_directory(
        directory,
        ignore_names=ignore or DEFAULT_IGNORE_NAMES,
        include_hidden=include_hidden,
    )
    if not converted:
        typer.echo("No .docx files were converted.")
    else:
        typer.echo(f"✓ Successfully converted {len(converted)} file(s) to PDF.")


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
