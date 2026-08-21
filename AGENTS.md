# AGENTS.md — hsutools

## Project Overview

**hsutools** is a Python CLI toolkit for file management and conversion. Version `1.2.1`, MIT license.

**Entry point**: `hsu` command (defined in `pyproject.toml` scripts)

## Quick Reference

```bash
# Install
poetry install
poetry install --extras s2tw  # with Chinese conversion support

# Run
poetry run hsu --help
poetry run hsu --lang zh --help  # Chinese interface

# Test
poetry run pytest

# Build
poetry build
poetry run hsu build-exe  # Windows exe (requires PyInstaller)
```

## Architecture

```
src/hsutools/
├── cli.py          # Typer CLI entry, command definitions, i18n integration
├── config.py       # Constants (extension buckets, ignore sets, image formats)
├── i18n.py         # Bilingual support (en/zh), env var HSU_LANG
├── utils.py        # Utility functions (path resolution, file iteration, PyInstaller wrapper)
└── core/
    ├── create_path.py      # Directory tree generation
    ├── docx_to_pdf.py      # DOCX → PDF conversion
    ├── file_manage.py      # File categorization
    ├── file_renamer.py     # Batch rename
    ├── image_resize.py     # Image resizing
    └── s2tw.py             # Simplified → Traditional Chinese (OpenCC)
```

## CLI Commands

| Command | Function | Key Dependencies |
|---------|----------|------------------|
| `hsu cpath` | Generate directory tree as Markdown | stdlib |
| `hsu filem` | Categorize files by date/prefix/suffix | stdlib |
| `hsu rename` | Batch rename files/dirs (text replace) | stdlib |
| `hsu topdf` | Convert .docx → .pdf | docx2pdf |
| `hsu resize` | Resize images (multiple formats) | Pillow |
| `hsu s2tw` | Simplified → Traditional Chinese | OpenCC (optional) |
| `hsu build-exe` | Build exe via PyInstaller | PyInstaller |

## Coding Conventions

### Style
- **Formatter/Linter**: No explicit config (ruff cache exists in .gitignore)
- **Type hints**: Used consistently (`from __future__ import annotations`)
- **String formatting**: f-strings preferred
- **Path handling**: `pathlib.Path` throughout (no `os.path`)

### Patterns
- **CLI layer** (`cli.py`): Thin — delegates to `core/` functions, handles i18n and user interaction
- **Core layer** (`core/`): Business logic, each module is independent
- **Config** (`config.py`): Constants only, no logic
- **Utils** (`utils.py`): Shared helpers, PyInstaller wrapper

### i18n
- All user-facing strings go through `tr()` function
- Keys are hierarchical: `command.option` (e.g., `cpath.path`)
- Two languages: `en` (default), `zh`
- Env var: `HSU_LANG=zh`

### Testing
- Framework: pytest + typer.testing.CliRunner
- Tests are in `tests/test_cli.py` (CLI integration tests)
- Use `tmp_path` fixture for filesystem tests
- Test naming: `test_<command>_<scenario>`

## Key Files to Know

| File | Purpose |
|------|---------|
| `cli.py` | Command definitions, `LocalizedGroup` for i18n help |
| `config.py` | `FILE_SUFFIX_BUCKETS` (166 extension mappings), `DEFAULT_IGNORE_NAMES` |
| `i18n.py` | `TEXTS` dict with all translations, `tr()` function |
| `core/s2tw.py` | Most complex module — `ConversionResult`, `ConversionStats` NamedTuples |

## Common Tasks

### Add a new CLI command
1. Add function in `cli.py` with `@app.command()`
2. Add i18n keys to `i18n.py` (`TEXTS` dict)
3. Add to `COMMAND_HELP_KEYS` and `OPTION_HELP_KEYS` in `cli.py`
4. Implement logic in `core/<module>.py`
5. Export from `core/__init__.py`
6. Add tests in `tests/test_cli.py`

### Add i18n support
1. Add key to `TEXTS` dict in `i18n.py` with `en` and `zh` values
2. Use `tr("key")` in code
3. Add to `COMMAND_HELP_KEYS` or `OPTION_HELP_KEYS` if it's a CLI option

## CI/CD

- **CI** (`.github/workflows/ci.yml`): Tests on push/PR to main, builds exe on Windows
- **Release** (`.github/workflows/release.yml`): Triggered by `v*.*.*` tags, publishes to PyPI, creates GitHub Release with artifacts

## Gotchas

1. **OpenCC is optional**: `s2tw` module handles missing import gracefully
2. **`test_demo/` directory**: Contains sample files, not part of tests
3. **`s2tw` extensions param**: CLI doesn't expose it yet (hardcoded `None` in cli.py:554)
4. **Bottom-up traversal**: `s2tw.py` uses `topdown=False` for safe directory renaming
