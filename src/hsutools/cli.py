from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import click
import typer

from typer.main import get_command

from . import __version__
from .config import DEFAULT_IGNORE_NAMES, DEFAULT_OUTPUT_FILE, DOCX_EXTENSION
from .core import categorize_files, convert_docx_directory, generate_path_md, replace_names, resize_images
from .utils import build_executable, resolve_directory, iter_files
from .i18n import ENV_LANG, get_lang, set_lang, tr


class LocalizedGroup(typer.core.TyperGroup):
    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        lang_value: Optional[str] = None
        for idx, token in enumerate(args):
            if token.startswith("--lang="):
                lang_value = token.split("=", 1)[1]
            elif token in {"--lang", "-l"} and idx + 1 < len(args):
                lang_value = args[idx + 1]
        if lang_value is None:
            lang_value = os.getenv(ENV_LANG)
        if lang_value:
            set_lang(lang_value)
        _apply_locale_to_command(self)
        return super().parse_args(ctx, args)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        _apply_locale_to_command(self)
        return super().format_help(ctx, formatter)


app = typer.Typer(cls=LocalizedGroup, help=tr("app.help"))


COMMAND_HELP_KEYS = {
    "app": "app.help",
    "cpath": "cpath.help",
    "filem": "filem.help",
    "rename": "rename.help",
    "topdf": "topdf.help",
    "resize": "resize.help",
    "build-exe": "buildexe.help",
}

OPTION_HELP_KEYS = {
    "app": {
        "lang": "option.lang",
        "version": "option.version",
    },
    "cpath": {
        "path": "cpath.path",
        "output": "cpath.output",
        "max_depth": "cpath.max_depth",
        "ignore": "cpath.ignore",
    },
    "filem": {
        "path": "filem.path",
        "mode": "filem.mode",
        "prefix": "filem.prefix",
        "ignore": "filem.ignore",
        "include_hidden": "filem.include_hidden",
    },
    "rename": {
        "path": "rename.path",
        "find_text": "rename.find",
        "replace_text": "rename.replace",
        "include_dirs": "rename.include_dirs",
        "ignore": "rename.ignore",
        "include_hidden": "rename.include_hidden",
    },
    "topdf": {
        "path": "topdf.path",
        "ignore": "topdf.ignore",
        "include_hidden": "topdf.include_hidden",
    },
    "resize": {
        "input": "resize.input",
        "output": "resize.output",
        "width": "resize.width",
        "height": "resize.height",
        "max_width": "resize.max_width",
        "max_height": "resize.max_height",
        "scale": "resize.scale",
        "keep_aspect": "resize.keep_aspect",
        "allow_upscale": "resize.allow_upscale",
        "quality": "resize.quality",
        "output_format": "resize.format",
        "suffix": "resize.suffix",
        "overwrite": "resize.overwrite",
        "recursive": "resize.recursive",
        "include_hidden": "resize.include_hidden",
        "ignore": "resize.ignore",
    },
    "build-exe": {
        "extra": "buildexe.extra",
    },
}


def _apply_locale_to_command(cmd: typer.models.CommandInfo | typer.core.TyperCommand) -> None:
    lang = get_lang()
    command_name = cmd.name or "app"
    if command_name == "main":
        command_name = "app"
    help_key = COMMAND_HELP_KEYS.get(command_name)
    if help_key:
        cmd.help = tr(help_key, lang=lang)

    opt_keys = OPTION_HELP_KEYS.get(command_name, {})
    for param in getattr(cmd, "params", []):
        key = opt_keys.get(param.name)
        if key:
            param.help = tr(key, lang=lang)
        # 處理 Typer/Click 內建選項
        elif isinstance(param, click.Option):
            if param.name == "install_completion":
                param.help = tr("option.install_completion", lang=lang)
            elif param.name == "show_completion":
                param.help = tr("option.show_completion", lang=lang)

    subcommands = getattr(cmd, "commands", {})
    for sub in subcommands.values():
        _apply_locale_to_command(sub)


def _lang_callback(value: Optional[str]) -> Optional[str]:
    set_lang(value)
    ctx = click.get_current_context(silent=True)
    if ctx and ctx.command:
        _apply_locale_to_command(ctx.command)
    return value


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"hsutools {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    lang: Optional[str] = typer.Option(  # noqa: B008
        None,
        "--lang",
        "-l",
        help=tr("option.lang"),
        case_sensitive=False,
        callback=_lang_callback,
        is_eager=True,
        envvar=ENV_LANG,
    ),
    version: Optional[bool] = typer.Option(  # noqa: B008
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help=tr("option.version"),
    ),
) -> None:
    """Root callback to support global options."""
    if lang:
        set_lang(lang)


@app.command(help=tr("cpath.help"))
def cpath(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help=tr("cpath.path")),
    output: str = typer.Option(DEFAULT_OUTPUT_FILE, help=tr("cpath.output")),
    max_depth: Optional[int] = typer.Option(None, help=tr("cpath.max_depth")),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help=tr("cpath.ignore"),
    ),
) -> None:
    directory = resolve_directory(path)
    output_path = generate_path_md(directory, output_file=output, ignore_names=ignore or DEFAULT_IGNORE_NAMES, max_depth=max_depth)
    typer.echo(tr("cpath.created", path=output_path))


@app.command(help=tr("filem.help"))
def filem(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help=tr("filem.path")),
    mode: Optional[str] = typer.Option(
        None,
        "--mode",
        "-m",
        case_sensitive=False,
        help=tr("filem.mode"),
    ),
    prefix: Optional[str] = typer.Option(None, help=tr("filem.prefix")),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help=tr("filem.ignore"),
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        is_flag=True,
        help=tr("filem.include_hidden"),
    ),
) -> None:
    if mode is None:
        mode = typer.prompt(
            tr("filem.prompt_mode"),
            type=typer.Choice(["date", "prefix", "suffix"], case_sensitive=False),
        )
    
    mode_value = mode.lower()
    if mode_value not in {"date", "prefix", "suffix"}:
        raise typer.BadParameter(tr("filem.invalid_mode"))
    
    # If mode is prefix and prefix not provided, prompt for it
    if mode_value == "prefix" and prefix is None:
        prefix = typer.prompt(tr("filem.prompt_prefix"))
        if prefix.strip() == "":
            prefix = None

    directory = resolve_directory(path)
    
    # Preview files to be moved
    files_to_move = list(iter_files(directory, ignore_names=ignore or DEFAULT_IGNORE_NAMES, include_hidden=include_hidden))
    
    if not files_to_move:
        typer.echo(tr("filem.none_found"))
        return
    
    typer.echo(f"\n{tr('filem.preview', count=len(files_to_move), mode=mode_value)}")
    typer.echo(tr("filem.directory", path=directory))
    
    # Show confirmation
    if not typer.confirm(f"\n{tr('filem.confirm')}", default=True):
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
        typer.echo(tr("filem.none_moved"))
    else:
        typer.echo(f"✓ {tr('filem.success', count=len(moved))}")


@app.command(help=tr("rename.help"))
def rename(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help=tr("rename.path")),
    find_text: Optional[str] = typer.Option(None, "--find", help=tr("rename.find")),
    replace_text: Optional[str] = typer.Option(None, "--replace", help=tr("rename.replace")),
    include_dirs: bool = typer.Option(
        False,
        "--include-dirs",
        is_flag=True,
        help=tr("rename.include_dirs"),
    ),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help=tr("rename.ignore"),
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        is_flag=True,
        help=tr("rename.include_hidden"),
    ),
) -> None:
    if find_text is None:
        find_text = typer.prompt(tr("rename.prompt_find"))
    if replace_text is None:
        replace_text = typer.prompt(tr("rename.prompt_replace"))
    
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
        typer.echo(tr("rename.none_found", text=find_text))
        return
    
    typer.echo(f"\n{tr('rename.preview_header', count=len(matching_entries))}")
    typer.echo(f"{tr('rename.find_replace', find=find_text, replace=replace_text)}\n")
    
    # Show preview (max 10 entries)
    for i, entry in enumerate(matching_entries[:10]):
        if entry.is_file():
            new_name = entry.stem.replace(find_text, replace_text) + entry.suffix
        else:
            new_name = entry.name.replace(find_text, replace_text)
        typer.echo(f"  {entry.name} → {new_name}")
    
    if len(matching_entries) > 10:
        typer.echo(f"  {tr('rename.more', count=len(matching_entries) - 10)}")
    
    # Confirmation
    if not typer.confirm(f"\n{tr('rename.confirm')}", default=True):
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
        typer.echo(tr("rename.none_updated"))
    else:
        typer.echo(f"✓ {tr('rename.success', count=len(updated))}")


@app.command(help=tr("topdf.help"))
def topdf(
    path: Path = typer.Option(".", exists=True, file_okay=False, dir_okay=True, help=tr("topdf.path")),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help=tr("topdf.ignore"),
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        is_flag=True,
        help=tr("topdf.include_hidden"),
    ),
) -> None:
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
        typer.echo(tr("topdf.none"))
        return
    
    typer.echo(f"\n{tr('topdf.preview', count=len(docx_files))}")
    for i, f in enumerate(docx_files[:10]):
        typer.echo(f"  {f.name}")
    if len(docx_files) > 10:
        typer.echo(f"  {tr('topdf.more', count=len(docx_files) - 10)}")
    
    # Confirmation
    if not typer.confirm(f"\n{tr('topdf.confirm')}", default=True):
        typer.echo("Operation cancelled.")
        return
    
    converted = convert_docx_directory(
        directory,
        ignore_names=ignore or DEFAULT_IGNORE_NAMES,
        include_hidden=include_hidden,
    )
    if not converted:
        typer.echo(tr("topdf.none_converted"))
    else:
        typer.echo(f"✓ {tr('topdf.success', count=len(converted))}")


@app.command(help=tr("resize.help"))
def resize(
    input: Path = typer.Option(
        ".",
        "--input",
        exists=True,
        file_okay=False,
        dir_okay=True,
        help=tr("resize.input"),
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        file_okay=False,
        dir_okay=True,
        help=tr("resize.output"),
    ),
    width: Optional[int] = typer.Option(1920, help=tr("resize.width")),
    height: Optional[int] = typer.Option(None, help=tr("resize.height")),
    max_width: Optional[int] = typer.Option(None, help=tr("resize.max_width")),
    max_height: Optional[int] = typer.Option(None, help=tr("resize.max_height")),
    scale: Optional[float] = typer.Option(None, help=tr("resize.scale")),
    keep_aspect: bool = typer.Option(True, help=tr("resize.keep_aspect")),
    allow_upscale: bool = typer.Option(False, "--allow-upscale", help=tr("resize.allow_upscale")),
    quality: int = typer.Option(90, help=tr("resize.quality")),
    output_format: Optional[str] = typer.Option(None, "--format", help=tr("resize.format")),
    suffix: Optional[str] = typer.Option(None, help=tr("resize.suffix")),
    overwrite: bool = typer.Option(False, "--overwrite", is_flag=True, help=tr("resize.overwrite")),
    recursive: bool = typer.Option(False, "--recursive", is_flag=True, help=tr("resize.recursive")),
    include_hidden: bool = typer.Option(False, "--include-hidden", is_flag=True, help=tr("resize.include_hidden")),
    ignore: list[str] = typer.Option(
        None,
        "--ignore",
        "-i",
        help=tr("resize.ignore"),
    ),
) -> None:
    if quality < 1 or quality > 100:
        raise typer.BadParameter(tr("resize.bad_quality"))

    if width is None and height is None and scale is None and max_width is None and max_height is None:
        raise typer.BadParameter(tr("resize.need_size"))

    source_dir = resolve_directory(input)
    written = resize_images(
        source_dir,
        output_dir=output,
        width=width,
        height=height,
        max_width=max_width,
        max_height=max_height,
        scale=scale,
        keep_aspect=keep_aspect,
        allow_upscale=allow_upscale,
        quality=quality,
        output_format=output_format,
        suffix=suffix,
        overwrite=overwrite,
        recursive=recursive,
        include_hidden=include_hidden,
        ignore_names=ignore or DEFAULT_IGNORE_NAMES,
    )

    if not written:
        typer.echo(tr("resize.none"))
        return

    typer.echo(f"✓ {tr('resize.success', count=len(written), output=written[0].parent)}")


@app.command("build-exe", help=tr("buildexe.help"))
def build_exe(
    extra: list[str] = typer.Option(
        None,
        "--extra-arg",
        help=tr("buildexe.extra"),
    ),
) -> None:
    code = build_executable(extra_args=extra)
    raise typer.Exit(code)


_apply_locale_to_command(get_command(app))


if __name__ == "__main__":
    app()
