# hsutools

Utilities for generating folder README trees, categorizing files, batch renaming, converting docx to pdf, and **Simplified to Traditional Chinese conversion**. The project now uses a standard `src/hsutools` package layout, Typer for the CLI, and Poetry for dependency management.

## Install

### With Poetry (local dev)
```bash
pip install poetry
poetry install
poetry run hsu --help
```

### Install with optional features
```bash
# Install with Simplified-to-Traditional Chinese conversion support
poetry install --extras s2tw
```

### From PyPI (after release)
```bash
pip install hsutools
hsu --help

# With optional features
pip install hsutools[s2tw]
```

### With pipx from the repo
```bash
pipx install .
hsu --help
```

## CLI usage

- `hsu cpath --path <dir> [--max-depth 3] [--ignore name ...]`
- `hsu filem --path <dir> --mode {date|prefix|suffix} [--prefix PREFIX]`
- `hsu rename --path <dir> --find old --replace new [--include-dirs]`
- `hsu topdf --path <dir> [--ignore name ...]`
- `hsu resize --path <dir> [--width 1920] [--height ...] [--format webp] [--recursive]`
- `hsu s2tw --path <dir|file> [--backup-dir ./backup] [--no-backup] [--no-convert-names]`
- `hsu --lang zh --help` 切換繁體說明；亦可用環境變數 `HSU_LANG=zh` 做預設
- `hsu build-exe [--extra-arg "--onefile"]` (requires `pyinstaller` in the Poetry dev group)

### Simplified to Traditional Chinese (`s2tw`)

Convert Simplified Chinese to Traditional Chinese (Taiwan) in files:
- **Automatic backup** of original files
- **Content conversion** using OpenCC
- **File/directory name conversion**
- **Recursive directory processing**

```bash
# Convert all supported text files in a directory (with backup)
hsu s2tw --path ./docs

# Convert without backup
hsu s2tw --path ./docs --no-backup

# Custom backup directory
hsu s2tw --path ./docs --backup-dir ./backup
```

**Requirements:**
```bash
pip install opencc-python-reimplemented
# OR install with extras
poetry install --extras s2tw
```

## Development

- Run tests: `poetry run pytest`
- Build artifacts: `poetry build`
- Optional exe: `poetry run hsu build-exe`
- Release: tag `v*.*.*` and GitHub Actions will build wheel/sdist, publish to PyPI (requires `PYPI_API_TOKEN` secret), and attach artifacts (wheel/sdist + Windows exe) to the GitHub Release.

## Project structure

```
hsutools/
├── pyproject.toml
├── src/hsutools/
│   ├── cli.py
│   ├── config.py
│   ├── utils.py
│   ├── i18n.py
│   └── core/
│       ├── create_path.py
│       ├── docx_to_pdf.py
│       ├── file_manage.py
│       ├── file_renamer.py
│       ├── image_resize.py
│       └── s2tw.py
└── tests/
	└── test_cli.py
```