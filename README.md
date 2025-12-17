# hsutools

Utilities for generating folder README trees, categorizing files, batch renaming, and converting docx to pdf. The project now uses a standard `src/hsutools` package layout, Typer for the CLI, and Poetry for dependency management.

## Install

### With Poetry (local dev)
```bash
pipx install poetry
poetry install
poetry run hsu --help
```

### From PyPI (after release)
```bash
pip install hsutools
hsu --help
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
- `hsu build-exe [--extra-arg "--onefile"]` (requires `pyinstaller` in the Poetry dev group)

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
│   └── core/
│       ├── create_path.py
│       ├── docx_to_pdf.py
│       ├── file_manage.py
│       └── file_renamer.py
└── tests/
	└── test_cli.py
```